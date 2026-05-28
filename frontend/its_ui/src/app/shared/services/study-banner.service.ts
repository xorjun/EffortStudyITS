import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { StudyBanner, StudyFunctionsService } from './study-functions.service';
import { StudyContextService } from './study-context.service';

@Injectable({
  providedIn: 'root'
})
export class StudyBannerService {
  private readonly currentBannerSubject = new BehaviorSubject<StudyBanner | null>(null);
  readonly currentBanner$ = this.currentBannerSubject.asObservable();

  private readonly firedEvents = new Set<string>();
  private sessionStartedAt = Date.now();
  private sawCodeRun = false;
  private sawError = false;
  private sawHintOpen = false;
  private refreshInFlight = false;
  private refreshFailures = 0;
  private bannerSupportDisabled = false;

  constructor(
    private studyFunctionsService: StudyFunctionsService,
    private studyContextService: StudyContextService,
  ) {
    window.setInterval(() => {
      void this.refresh();
    }, 60000);

    this.studyContextService.state$.subscribe((state) => {
      if (state.initialized) {
        this.markSessionStarted();
      }
    });
  }

  markSessionStarted(): void {
    if (!this.isBannerSupportEnabled()) {
      this.currentBannerSubject.next(null);
      return;
    }

    this.sessionStartedAt = Date.now();
    this.firedEvents.clear();
    this.sawCodeRun = false;
    this.sawError = false;
    this.sawHintOpen = false;
    this.refreshFailures = 0;
    this.firedEvents.add('session-arrival');
    void this.refresh(true);
  }

  registerEvent(eventType: string): void {
    if (!this.isBannerSupportEnabled()) {
      return;
    }

    this.firedEvents.add(eventType);
    if (eventType === 'code-run' && !this.sawCodeRun) {
      this.sawCodeRun = true;
      this.firedEvents.add('first-code-run');
    }
    if (eventType === 'error' && !this.sawError) {
      this.sawError = true;
      this.firedEvents.add('first-error');
    }
    if (eventType === 'hint-open' && !this.sawHintOpen) {
      this.sawHintOpen = true;
      this.firedEvents.add('first-hint-open');
    }
    void this.refresh();
  }

  async submitCurrentResponse(responseData: Record<string, unknown>, wasDismissed = false): Promise<void> {
    if (!this.isBannerSupportEnabled()) {
      return;
    }

    const banner = this.currentBannerSubject.value;
    if (!banner) {
      return;
    }

    await this.studyFunctionsService.submitBannerResponse(banner.id, banner.shownAt, responseData, wasDismissed);
    this.currentBannerSubject.next(null);
  }

  private async refresh(force = false): Promise<void> {
    if (!this.isBannerSupportEnabled()) {
      this.currentBannerSubject.next(null);
      return;
    }

    if (this.refreshInFlight || (!force && this.currentBannerSubject.value)) {
      return;
    }

    this.refreshInFlight = true;
    try {
      const banners = await this.studyFunctionsService.checkBanners(
        Array.from(this.firedEvents),
        Math.floor((Date.now() - this.sessionStartedAt) / 60000),
      );
      this.refreshFailures = 0;
      this.currentBannerSubject.next(banners[0] || null);
    } catch {
      this.refreshFailures += 1;
      if (this.refreshFailures >= 3) {
        this.bannerSupportDisabled = true;
        this.currentBannerSubject.next(null);
      }
    } finally {
      this.refreshInFlight = false;
    }
  }

  private isBannerSupportEnabled(): boolean {
    return this.studyFunctionsService.isConfigured
      && this.studyContextService.snapshot.initialized
      && !this.bannerSupportDisabled;
  }
}
