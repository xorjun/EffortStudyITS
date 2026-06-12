import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable, Subscription, interval } from 'rxjs';

/**
 * Tracks the wall-clock time since the current tutoring task started and
 * exposes it as a reactive stream. Components that need to gate UI on
 * "at least N minutes into the current task" (e.g. reveal the Next Task
 * button after a frustration timeout) subscribe to `secondsSinceStart$`
 * and decide locally.
 *
 * Each new task resets the timer back to zero via `markSessionStarted()`.
 * This way, a learner who advances to a new task (via the visible Next
 * Task button or the secret Ctrl+Shift+Q shortcut) starts the 5-minute
 * no-skip window over again on the new task.
 *
 * The 1Hz tick is started lazily — the first subscribe starts the
 * interval; when the last subscriber unsubscribes, the interval is
 * disposed. This keeps the page idle when no component is observing
 * the timer.
 */
@Injectable({
  providedIn: 'root'
})
export class SessionTimerService implements OnDestroy {
  private static readonly STORAGE_KEY = 'sessionStartedAt';

  private sessionStartedAt: number;
  private readonly secondsSubject = new BehaviorSubject<number>(0);
  /** Seconds elapsed since the current task started, emitted every second. */
  readonly secondsSinceStart$: Observable<number> = this.secondsSubject.asObservable();
  private tickSubscription?: Subscription;
  /** How many consumers are currently subscribed to secondsSinceStart$. */
  private subscriberCount = 0;

  constructor() {
    const stored = this.readStoredStart();
    this.sessionStartedAt = stored ?? Date.now();
    if (stored === null) {
      this.writeStoredStart(this.sessionStartedAt);
    }
    // No ticker started eagerly. The first subscribe below starts it;
    // the last unsubscribe stops it.
  }

  /**
   * Reset the task start to the current time. Called on every new task
   * fetch so the 5-minute no-skip window applies per task, not per
   * study session. After a Ctrl+Shift+Q skip, the next task's Next Task
   * button will be hidden for its first 5 minutes as expected.
   */
  markSessionStarted(): void {
    this.sessionStartedAt = Date.now();
    this.writeStoredStart(this.sessionStartedAt);
    this.emit();
  }

  /** Convenience: seconds elapsed since the current task started. */
  getSecondsSinceStart(): number {
    return Math.max(0, Math.floor((Date.now() - this.sessionStartedAt) / 1000));
  }

  /**
   * Subscribe to the tick stream. The first call starts the underlying
   * 1Hz interval; the last call to unsubscribe stops it.
   *
   * We do not use BehaviorSubject's subscribe directly because we need
   * to track the subscriber count to know when to dispose the
   * interval. The returned Subscription is a small wrapper that
   * decrements the count on unsubscribe.
   */
  subscribe(observer: (value: number) => void): Subscription {
    this.subscriberCount += 1;
    if (this.subscriberCount === 1) {
      this.startTicking();
    }
    const inner = this.secondsSubject.subscribe(observer);
    return new Subscription(() => {
      inner.unsubscribe();
      this.subscriberCount = Math.max(0, this.subscriberCount - 1);
      if (this.subscriberCount === 0) {
        this.stopTicking();
      }
    });
  }

  ngOnDestroy(): void {
    this.stopTicking();
    this.secondsSubject.complete();
  }

  private startTicking(): void {
    this.emit();
    this.tickSubscription = interval(1000).subscribe(() => this.emit());
  }

  private stopTicking(): void {
    this.tickSubscription?.unsubscribe();
    this.tickSubscription = undefined;
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
      // localStorage may be unavailable (private mode) — the in-memory
      // value still works for the current page lifetime.
    }
  }
}
