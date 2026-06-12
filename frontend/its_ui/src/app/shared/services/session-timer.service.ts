import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable, Subscription, interval } from 'rxjs';

/**
 * Tracks the wall-clock time since the current tutoring session started and
 * exposes it as a reactive stream. Components that need to gate UI on
 * "at least N minutes into the session" (e.g. reveal the Next Task button
 * after a frustration timeout) subscribe to `secondsSinceStart$` and decide
 * locally.
 *
 * "Session started" is whichever happens first:
 *  - the StudyContextService state becomes initialized (study context
 *    resolved from URL or sessionStorage), or
 *  - a caller explicitly invokes `markSessionStarted()` (e.g. when the
 *    tutoring view mounts and the first task is fetched).
 *
 * The timer persists in localStorage so the 5-minute countdown survives a
 * page refresh mid-session.
 */
@Injectable({
  providedIn: 'root'
})
export class SessionTimerService implements OnDestroy {
  private static readonly STORAGE_KEY = 'sessionStartedAt';

  private sessionStartedAt: number;
  private readonly secondsSubject = new BehaviorSubject<number>(0);
  /** Seconds elapsed since the current session started, emitted every second. */
  readonly secondsSinceStart$: Observable<number> = this.secondsSubject.asObservable();
  private tickSubscription?: Subscription;

  constructor() {
    const stored = this.readStoredStart();
    this.sessionStartedAt = stored ?? Date.now();
    if (stored === null) {
      this.writeStoredStart(this.sessionStartedAt);
    }
    this.startTicking();
  }

  /**
   * Reset the session start to the current time. Called when the tutoring
   * view is entered for the first time, or when the study context is
   * initialized from the URL.
   */
  markSessionStarted(): void {
    const now = Date.now();
    // Only reset if we don't already have a stored start, or if more than
    // 30 minutes have passed (treat as a new session).
    const stored = this.readStoredStart();
    if (stored === null || (now - stored) > 30 * 60 * 1000) {
      this.sessionStartedAt = now;
      this.writeStoredStart(now);
    } else {
      this.sessionStartedAt = stored;
    }
    this.emit();
  }

  /** Convenience: seconds elapsed since the current session started. */
  getSecondsSinceStart(): number {
    return Math.max(0, Math.floor((Date.now() - this.sessionStartedAt) / 1000));
  }

  ngOnDestroy(): void {
    this.tickSubscription?.unsubscribe();
  }

  private startTicking(): void {
    this.emit();
    this.tickSubscription = interval(1000).subscribe(() => this.emit());
  }

  private emit(): void {
    this.secondsSubject.next(this.getSecondsSinceStart());
  }

  private readStoredStart(): number | null {
    try {
      const raw = localStorage.getItem(SessionTimerService.STORAGE_KEY);
      if (!raw) {
        return null;
      }
      const n = Number.parseInt(raw, 10);
      return Number.isNaN(n) ? null : n;
    } catch {
      return null;
    }
  }

  private writeStoredStart(value: number): void {
    try {
      localStorage.setItem(SessionTimerService.STORAGE_KEY, String(value));
    } catch {
      // localStorage may be unavailable (private mode) — the in-memory value
      // still works for the current page lifetime.
    }
  }
}
