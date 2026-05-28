import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { SafeResourceUrl, DomSanitizer } from '@angular/platform-browser';
import { environment } from 'src/environments/environment';
import { EventShareService } from '../shared/services/event-share.service';
import { StudyContextService } from '../shared/services/study-context.service';
import { StudyFunctionsService } from '../shared/services/study-functions.service';
import { StudyTelemetryService } from '../shared/services/study-telemetry.service';

interface ActivityTrackerDemo {
  available: boolean;
  rememberedSubject?: string;
  sessions?: [string, number][];
  showSessionsOutput?: string[];
  firstSessionDescription?: string;
  totalMinutes?: number;
  recommendation?: string;
  reason?: string;
}

@Component({
  selector: 'app-final-showcase',
  templateUrl: './final-showcase.component.html',
  styleUrls: ['./final-showcase.component.css'],
  imports: [CommonModule]
})
export class FinalShowcaseComponent implements OnInit, OnDestroy {
  latestCode = '';
  demoUrl: SafeResourceUrl | null = null;
  demoUnavailableReason: string | null = null;
  activityTrackerDemo: ActivityTrackerDemo | null = null;
  activityTrackerDemoError: string | null = null;

  sessionCompletionPending = false;
  sessionCompletionError: string | null = null;
  sessionDownloadUrl: string | null = null;
  sessionSurveyUrl: string | null = null;
  sessionPreviewUrl: string | null = null;

  private demoBlobUrl: string | null = null;

  constructor(
    private sanitizer: DomSanitizer,
    private client: HttpClient,
    private eventShareService: EventShareService,
    public studyContextService: StudyContextService,
    public studyFunctionsService: StudyFunctionsService,
    private studyTelemetryService: StudyTelemetryService,
  ) {}

  get canPrepareSessionPackage(): boolean {
    return this.studyFunctionsService.isConfigured && this.studyContextService.snapshot.initialized;
  }

  ngOnInit(): void {
    this.latestCode = sessionStorage.getItem('latestCode') || '';
    this.sessionDownloadUrl = sessionStorage.getItem('sessionDownloadUrl');
    this.sessionSurveyUrl = sessionStorage.getItem('sessionSurveyUrl');
    this.sessionPreviewUrl = sessionStorage.getItem('sessionPreviewUrl');

    this.buildLocalDemo(this.latestCode);
    if (!this.demoUrl && sessionStorage.getItem('courseID') === 'activity_tracker') {
      this.loadActivityTrackerDemo();
    }
    this.studyTelemetryService.logContextEvent('final-showcase-opened', {
      hasCode: this.latestCode.length > 0,
      hasRenderableDemo: !!this.demoUrl,
    });
  }

  ngOnDestroy(): void {
    if (this.demoBlobUrl) {
      URL.revokeObjectURL(this.demoBlobUrl);
    }
  }

  async prepareSessionPackage(): Promise<void> {
    if (!this.canPrepareSessionPackage || this.sessionCompletionPending) {
      return;
    }

    this.sessionCompletionPending = true;
    this.sessionCompletionError = null;

    try {
      const response = await this.studyFunctionsService.completeCurrentSession(this.latestCode);
      this.sessionDownloadUrl = this.studyFunctionsService.getDownloadUrl(response.fileId);
      this.sessionSurveyUrl = response.surveyUrl;

      sessionStorage.setItem('sessionDownloadUrl', this.sessionDownloadUrl);
      sessionStorage.setItem('sessionSurveyUrl', this.sessionSurveyUrl || '');

      this.client.post<any>(
        `${environment.apiUrl}/info/final_preview_link`,
        {
          code: this.buildPreviewSource(),
          title: this.activityTrackerDemo ? 'Activity Tracker Demo Preview' : 'Final Activity Tracker Demo',
        },
        { withCredentials: true }
      ).subscribe({
        next: (previewResponse) => {
          this.sessionPreviewUrl = previewResponse.preview_url || null;
          if (this.sessionPreviewUrl) {
            sessionStorage.setItem('sessionPreviewUrl', this.sessionPreviewUrl);
          }
        },
        error: () => {
          this.sessionPreviewUrl = null;
          this.sessionCompletionError = 'Preview link could not be created. Your local demo is still available below.';
        }
      });

      this.studyTelemetryService.logContextEvent('session-complete', {
        downloadReady: true,
        previewReady: true,
      });
    } catch {
      this.sessionCompletionError = 'Preparing the session archive failed.';
    } finally {
      this.sessionCompletionPending = false;
    }
  }

  backToCourses(): void {
    this.eventShareService.emitViewChange('homeRequest');
  }

  private buildLocalDemo(code: string): void {
    this.demoUrl = null;
    this.demoUnavailableReason = null;
    const lower = code.toLowerCase();
    const looksLikeWebApp = lower.includes('<html') || lower.includes('<body') || lower.includes('<script') || lower.includes('<div');

    if (!looksLikeWebApp) {
      this.demoUnavailableReason = 'No browser-runnable HTML app was detected in your latest code. Continue editing your final exercise and try again.';
      return;
    }

    this.demoBlobUrl = URL.createObjectURL(new Blob([code], { type: 'text/html' }));
    this.demoUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.demoBlobUrl);
    this.demoUnavailableReason = null;
  }

  private loadActivityTrackerDemo(): void {
    this.client.get<ActivityTrackerDemo>(`${environment.apiUrl}/info/activity_tracker_demo`, { withCredentials: true }).subscribe({
      next: (demo) => {
        if (demo.available) {
          this.activityTrackerDemo = demo;
          this.activityTrackerDemoError = null;
          this.demoUnavailableReason = null;
        } else {
          this.activityTrackerDemo = null;
          this.activityTrackerDemoError = demo.reason || 'The Activity Tracker demo is not available yet.';
        }
        this.studyTelemetryService.logContextEvent('final-showcase-activity-demo', {
          available: demo.available,
          sessionCount: Array.isArray(demo.sessions) ? demo.sessions.length : 0,
        });
      },
      error: () => {
        this.activityTrackerDemo = null;
        this.activityTrackerDemoError = 'The Activity Tracker demo could not be generated from your saved solutions.';
      }
    });
  }

  private buildPreviewSource(): string {
    if (this.activityTrackerDemo?.available) {
      return this.buildActivityTrackerPreviewHtml(this.activityTrackerDemo);
    }
    return this.latestCode;
  }

  private buildActivityTrackerPreviewHtml(demo: ActivityTrackerDemo): string {
    const sessionItems = (demo.sessions || [])
      .map(([subject, duration]) => `<li>${this.escapeHtml(subject)} - ${duration} minutes</li>`)
      .join('');
    const outputLines = (demo.showSessionsOutput || [])
      .map((line) => this.escapeHtml(line))
      .join('<br />');

    return `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Activity Tracker Demo</title>
    <style>
      body { font-family: ui-sans-serif, system-ui, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
      main { max-width: 820px; margin: 0 auto; padding: 24px; }
      .hero, .card { background: rgba(15, 23, 42, 0.86); border: 1px solid rgba(148, 163, 184, 0.24); border-radius: 16px; padding: 18px; margin-bottom: 16px; }
      h1, h2, p { margin-top: 0; }
      ul { padding-left: 20px; }
      pre { background: #020617; border-radius: 12px; padding: 14px; overflow: auto; }
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <p>Course Finished</p>
        <h1>Activity Tracker Demo</h1>
        <p>${this.escapeHtml(demo.recommendation || '')}</p>
      </section>
      <section class="card">
        <h2>Remembered Subject</h2>
        <p>${this.escapeHtml(demo.rememberedSubject || '')}</p>
        <h2>Saved Sessions</h2>
        <ul>${sessionItems}</ul>
      </section>
      <section class="card">
        <h2>Computed Summary</h2>
        <p>${this.escapeHtml(demo.firstSessionDescription || '')}</p>
        <p>Total Study Time: ${demo.totalMinutes ?? 0} minutes</p>
      </section>
      <section class="card">
        <h2>show_sessions Output</h2>
        <pre>${outputLines}</pre>
      </section>
    </main>
  </body>
</html>`;
  }

  private escapeHtml(value: string): string {
    return value
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }
}
