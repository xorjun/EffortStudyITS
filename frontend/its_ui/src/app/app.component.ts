import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { EventShareService } from './shared/services/event-share.service';
import { environment } from 'src/environments/environment';
import { CourseSettingsService } from './shared/services/course-settings-service.service';
import { AuthComponent } from './auth/auth.component';
import { ProfileComponent } from './profile/profile.component';
import { NavigationBarComponent } from './navigation-bar/navigation-bar.component';
import { TaskPanelComponent } from './task-panel/task-panel.component';
import { FeedbackPanelComponent } from './feedback-panel/feedback-panel.component';
import { CodePanelComponent } from './code-panel/code-panel.component';
import { CourseSelectionPanelComponent } from './course-selection-panel/course-selection-panel.component';
import { CourseSettingsComponent } from './course-settings/course-settings.component';
import { SkillOverviewComponent } from './skill-overview/skill-overview.component';
import { AdminSettingsComponent } from './admin-settings/admin-settings.component';
import { FinalShowcaseComponent } from './final-showcase/final-showcase.component';
import { AngularSplitModule } from 'angular-split';
import { StudyFunctionsService } from './shared/services/study-functions.service';
import { StudyTelemetryService } from './shared/services/study-telemetry.service';
import { StudyBannerComponent } from './study-banner/study-banner.component';
import { CourseIntroComponent } from './course-intro/course-intro.component';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],
    imports: [
        CommonModule,
        AngularSplitModule,
        AuthComponent,
        ProfileComponent,
        NavigationBarComponent,
        TaskPanelComponent,
        FeedbackPanelComponent,
        CodePanelComponent,
        CourseSelectionPanelComponent,
        CourseSettingsComponent,
        SkillOverviewComponent,
        AdminSettingsComponent,
        FinalShowcaseComponent,
        StudyBannerComponent,
        CourseIntroComponent
    ]
})
export class AppComponent {

  title = 'Tutoring System for Programming';
  pageName = 'loginView'
  originPage = ''
  initTask?: string | null;
  course?: any

  constructor(private client: HttpClient,
    private eventShareService: EventShareService,
    private courseSettingsService: CourseSettingsService,
    private studyFunctionsService: StudyFunctionsService,
    private studyTelemetryService: StudyTelemetryService){
      eventShareService.viewChange$.subscribe(
        (status) => {
          this.setView(status);
        }
      );
  }

  ngOnInit(): void {
    // Fire-and-forget health check, scheduled via requestIdleCallback so
    // it does not compete with the first paint.
    this.runWhenIdle(() => {
      this.client.get<any>(`${environment.apiUrl}/status`).subscribe({
        next: (data) => { console.log(data["message"]); },
        error: () => { /* health-check is best-effort */ }
      });
    });

    // The Prolific participant flow does its own auth via
    // /api/auth/auto-login-by-pid inside initializeFromUrl. A direct
    // visit (no PROLIFIC_PID) is the only case where the /users/me
    // probe is useful, and even there we delay it slightly so the
    // first paint is not blocked.
    const params = new URLSearchParams(window.location.search);
    const hasProlificPid = !!params.get('PROLIFIC_PID');
    if (!hasProlificPid) {
      this.runWhenIdle(() => {
        this.client.get<any>(`${environment.apiUrl}/users/me`, { withCredentials: true }).subscribe({
          next: () => { this.setView('loggedIn'); },
          error: () => { /* not authenticated — stay on loginView */ }
        });
      });
    }

    void this.studyFunctionsService.initializeFromUrl().then((result) => {
      if (result) {
        this.studyTelemetryService.logEvent('session-start', {
          sessionNumber: result.currentSession,
          condition: result.condition,
        }, result.currentSession);
        const prolificPid = params.get('PROLIFIC_PID');
        if (prolificPid) {
          void this.studyFunctionsService.loginScriptByProlificId(prolificPid).then(() => {
            this.client.get<any>(`${environment.apiUrl}/users/me`, { withCredentials: true }).subscribe({
              next: () => { this.setView('loggedIn'); },
              error: () => { /* stay on the current view */ }
            });
          });
        }
      }
    });
  }

  /**
   * Schedule a callback to run when the browser is idle. Falls back to
   * a short setTimeout(0) in environments where requestIdleCallback
   * is not available.
   */
  private runWhenIdle(callback: () => void): void {
    if (typeof (window as any).requestIdleCallback === 'function') {
      (window as any).requestIdleCallback(callback, { timeout: 2000 });
    } else {
      setTimeout(callback, 0);
    }
  }

  //TODO: Make origin-page a stack in order to enable navigating through navbar. 
  setView(status: string) {
    switch (status) {
      case 'loggedIn':
          this.pageName = 'welcomePage';
          break;
      case 'loggedOut':
          this.pageName = 'loginView';
          break;
      case 'courseSelected':
          this.courseSettingsService.getCourse().subscribe((course: any) => {
            this.course = course;
            if (course.introduction) {
              this.pageName = 'courseIntroView';
            } else {
              this.pageName = 'tutoringView';
            }
          });
          break;
      case 'introCompleted':
          this.pageName = 'tutoringView';
          break;
      case 'skillOverviewRequest':
        this.pageName = 'skillOverview'
        break;
      case 'closedProfile':
        this.initTask = sessionStorage.getItem("taskId")!;
        this.pageName = this.originPage;
        this.originPage = "";
        break;
      case 'profileRequest':
        this.originPage = this.pageName
        this.pageName = 'profileView';
        break;
      case 'homeRequest':
        this.pageName = 'welcomePage';
        this.initTask = null;
        break;
      case 'courseSettingsRequest':
        this.originPage = "tutoringView";
        this.pageName = 'courseSettings';
        break;
      case 'adminSettingsRequest':
          this.originPage = this.pageName;
          this.pageName = 'adminSettings';
          break;
      case 'finalShowcase':
        this.pageName = 'finalShowcase';
        break;
      case 'settingsClosed':
        if (this.originPage == "tutoringView")
          {this.initTask = sessionStorage.getItem("taskId")!;}
        this.pageName = this.originPage;
        this.originPage = "";
        break;
      default:
        this.pageName = 'loginView'
          console.log("Invalid View request");
          break;
    }
  }
}
