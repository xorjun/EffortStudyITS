import { Injectable } from '@angular/core';
import { Account, Client, Databases, ExecutionMethod, Functions, Storage, Teams } from 'appwrite';
import { RuntimeConfigService } from './runtime-config.service';

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

  async ensureAnonymousSession(): Promise<void> {
    if (!this.isConfigured) {
      return;
    }

    try {
      await this.account.get();
    } catch {
      await this.account.createAnonymousSession();
    }
  }

  async createJwt(): Promise<string> {
    const jwt = await this.account.createJWT();
    return jwt.jwt;
  }

  async createEmailSession(email: string, password: string): Promise<void> {
    await this.account.createEmailPasswordSession(email, password);
  }
}
