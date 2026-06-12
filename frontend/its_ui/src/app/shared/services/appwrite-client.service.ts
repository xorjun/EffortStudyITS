import { Injectable } from '@angular/core';
import { Account, Client, Databases, ExecutionMethod, Functions, Storage, Teams } from 'appwrite';
import { RuntimeConfigService } from './runtime-config.service';

/**
 * Storage key under which we cache the per-PID Appwrite password. The
 * password is generated once on the participant's first visit and never
 * leaves the browser. The same password is reused on every subsequent
 * visit from the same browser.
 */
const PID_PASSWORD_STORAGE_PREFIX = 'its.prolific.password.';

@Injectable({
  providedIn: 'root'
})
export class AppwriteClientService {
  private readonly clientInstance = new Client();

  readonly account = new Account(this.clientInstance);
  readonly databases = new Databases(this.clientInstance);
  readonly functions = new Functions(this.clientInstance);
  readonly storage = new Storage(this.clientInstance);
  readonly teams = new Teams(this.clientInstance);
  readonly executionMethod = ExecutionMethod;

  constructor(private runtimeConfigService: RuntimeConfigService) {
    const config = this.runtimeConfigService.appwrite;
    if (config.endpoint) {
      this.clientInstance.setEndpoint(config.endpoint);
    }
    if (config.projectId) {
      this.clientInstance.setProject(config.projectId);
    }
  }

  get client(): Client {
    return this.clientInstance;
  }

  get isConfigured(): boolean {
    const config = this.runtimeConfigService.appwrite;
    return config.endpoint.trim().length > 0 && config.projectId.trim().length > 0;
  }

  setJwt(jwt: string): void {
    this.clientInstance.setJWT(jwt);
  }

  /**
   * Deterministic Appwrite userId derived from a Prolific PID. The same
   * PID always resolves to the same Appwrite user, so the PID is the
   * single tying key across every pipeline component (Appwrite, SCRIPT,
   * MongoDB, SoSci).
   *
   * Appwrite userIds must be 1-36 chars, alphanumeric plus `-`, `_`,
   * `.`. We use a hex-encoded FNV-1a hash of the PID truncated to 36
   * chars. Not used for security; the goal is determinism and uniqueness
   * across participants.
   */
  static pidToUserId(prolificPid: string): string {
    if (!prolificPid) {
      throw new Error('pidToUserId: prolificPid is required');
    }
    let h1 = 0x811c9dc5;
    let h2 = 0xcafebabe;
    for (let i = 0; i < prolificPid.length; i += 1) {
      const ch = prolificPid.charCodeAt(i);
      h1 = (h1 ^ ch) >>> 0;
      h1 = ((h1 + ((h1 << 1) + (h1 << 4) + (h1 << 7) + (h1 << 8) + (h1 << 24))) >>> 0);
      h2 = (h2 ^ (ch + i)) >>> 0;
      h2 = ((h2 + ((h2 << 2) + (h2 << 6) + (h2 << 11) + (h2 << 14) + (h2 << 25))) >>> 0);
    }
    const hex = (h1.toString(16).padStart(8, '0') + h2.toString(16).padStart(8, '0'));
    // Pad to 36 chars if PID is unusually short, otherwise use the first 36 hex chars.
    return (hex + hex + hex).slice(0, 36);
  }

  static pidToEmail(prolificPid: string): string {
    return `prolific+${prolificPid}@scriptorium.local`;
  }

  private getCachedPassword(prolificPid: string): string | null {
    try {
      return localStorage.getItem(PID_PASSWORD_STORAGE_PREFIX + prolificPid);
    } catch {
      return null;
    }
  }

  private cachePassword(prolificPid: string, password: string): void {
    try {
      localStorage.setItem(PID_PASSWORD_STORAGE_PREFIX + prolificPid, password);
    } catch {
      // localStorage may be unavailable (private mode) — the participant
      // will be a different Appwrite user next time and a new participant
      // document will be created. Acceptable for the dev/CI case.
    }
  }

  private generatePassword(): string {
    // 24 random bytes → 32 hex chars. Sufficient entropy for an account
    // that is only ever used to sign into Appwrite from this same browser.
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
      const bytes = new Uint8Array(24);
      crypto.getRandomValues(bytes);
      return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('').slice(0, 32);
    }
    return Math.random().toString(36).slice(2).padEnd(32, '0');
  }

  /**
   * Ensure an Appwrite session is established for the given Prolific PID.
   *
   * Flow:
   *  1. If a valid Appwrite session already exists and the Appwrite user's
   *     identity matches the requested PID's deterministic userId, reuse it.
   *  2. Otherwise: ensure an Appwrite user with the deterministic userId
   *     and email exists. If the user does not exist, create it with a
   *     freshly generated password cached in localStorage.
   *  3. Sign in with the email+password to create a real session.
   *
   * No anonymous session is ever created. The Prolific PID is the single
   * tying key across all pipeline components.
   */
  async ensureProlificSession(prolificPid: string): Promise<void> {
    if (!this.isConfigured) {
      return;
    }
    if (!prolificPid) {
      return;
    }

    const expectedUserId = AppwriteClientService.pidToUserId(prolificPid);
    const email = AppwriteClientService.pidToEmail(prolificPid);

    // Step 1: try the existing session.
    try {
      const current = await this.account.get();
      if (current.$id === expectedUserId) {
        return;
      }
      // Session belongs to a different PID. Drop it and re-sign.
      await this.account.deleteSession('current').catch(() => undefined);
    } catch {
      // No current session, fall through.
    }

    // Step 2: ensure a user exists for this PID.
    const password = this.getCachedPassword(prolificPid) || this.generatePassword();
    if (!this.getCachedPassword(prolificPid)) {
      this.cachePassword(prolificPid, password);
    }
    try {
      // Try to create the user. If it already exists (409), this is fine.
      // account.create takes positional args: (userId, email, password, name?).
      await this.account.create(expectedUserId, email, password, prolificPid);
    } catch (error: any) {
      // 409 / user_already_exists means the user already exists — the
      // cached password is presumably correct and we can sign in. Other
      // errors propagate.
      if (error?.code !== 409 && error?.type !== 'user_already_exists') {
        throw error;
      }
    }

    // Step 3: sign in.
    await this.account.createEmailPasswordSession(email, password);
  }

  /**
   * @deprecated Use `ensureProlificSession(pid)` instead. Retained as a
   * thin shim for callers that have not yet been migrated.
   */
  async ensureAnonymousSession(): Promise<void> {
    // No-op in the PID-only model. Callers should pass the PID explicitly.
  }

  async createJwt(): Promise<string> {
    const jwt = await this.account.createJWT();
    return jwt.jwt;
  }

  async createEmailSession(email: string, password: string): Promise<void> {
    await this.account.createEmailPasswordSession(email, password);
  }
}
