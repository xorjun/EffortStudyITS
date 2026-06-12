import { Component, EventEmitter, Output, Input, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EventShareService } from '../shared/services/event-share.service';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { RolesService } from '../shared/services/roles.service';
import { CourseSettingsService } from '../shared/services/course-settings-service.service';
import { Subscription } from 'rxjs';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MarkdownDialogService } from '../shared/services/markdown-dialog.service';
import { TaskStatusService } from '../shared/services/task-status.service';
import { HelpDialogService } from '../shared/services/help-dialog.service';
import { SessionTimerService } from '../shared/services/session-timer.service';
import { StudyTelemetryService } from '../shared/services/study-telemetry.service';

@Component({
    selector: 'app-navigation-bar',
    templateUrl: './navigation-bar.component.html',
    styleUrls: ['./navigation-bar.component.css'],
    imports: [
        CommonModule,
        MatIconModule,
        MatToolbarModule,
        MatButtonModule,
        MatMenuModule,
        MatDividerModule,
        MatTooltipModule
    ]
})
export class NavigationBarComponent {

  @Output() profileButtonClicked: EventEmitter<string> = new EventEmitter<string>;
  @Output() homeButtonClicked: EventEmitter<string> = new EventEmitter<string>;
  @Output() settingButtonClicked: EventEmitter<string> = new EventEmitter<string>;

  taskFetchedSubscription: Subscription;
  topicInducedSubscription: Subscription;
  sessionTimerSubscription: Subscription;

  apiUrl: string = environment.apiUrl;
  user_name: string = "INVALID_EMAIL";
  title: string = 'SCRIPT'
  task_name: string = '';
  course?: any;
  course_topics: string[] = [];
  current_topic: string = "";
  current_topic_index: number = 0;

  roles: string[] = [];

  display_elements: Set<string> = new Set(); 
  _currentPageName?: string

  local_curriculum: string[] = [];
  task_status_dict: { [taskName: string]: string } = {};

  visibleBubbles: string[] = [];
  showLeftEllipsis: boolean = false;
  showRightEllipsis: boolean = false;

  /**
   * Number of seconds elapsed since the current session started. Updated
   * once per second by `SessionTimerService` so the Next Task button can
   * be gated on a 5-minute frustration timeout.
   */
  secondsSinceSessionStart: number = 0;

  /**
   * The Next Task button is hidden for the first 5 minutes of every
   * session. After that it becomes visible so a frustrated learner who
   * has been stuck for a while can move on without giving up on the
   * platform.
   */
  private static readonly NEXT_TASK_UNLOCK_SECONDS = 5 * 60;

  constructor(
    private eventShareService: EventShareService,
    private httpClient: HttpClient,
    private rolesService: RolesService,
    private courseSettingsService: CourseSettingsService,
    private markdownDialogService: MarkdownDialogService,
    private taskStatusService: TaskStatusService,
    private helpDialogService: HelpDialogService,
    private sessionTimerService: SessionTimerService,
    private studyTelemetryService: StudyTelemetryService,
    ){
      this.taskFetchedSubscription = this.eventShareService.newTaskFetched$.subscribe(
        () => {
          // First task of the session: anchor the session start so the
          // Next Task button can be hidden during the initial 5-minute
          // "no-skip" window.
          this.sessionTimerService.markSessionStarted();
          this.task_name = sessionStorage.getItem("taskId")!
          if (this.course == undefined || this.course.unique_name != sessionStorage.getItem("CourseID")) {
            console.log("fetching course.")
            this.courseSettingsService.getCourse().subscribe((course) =>
              {
                this.course = course;
                this.updateTopics();
                this.updateDisplayElements();
                this.fetchTaskStatus();
              });
          } else {
            this.fetchTaskStatus();
          }
        });
      // Keep the Next Task button tooltip in sync with the live countdown.
      // We use SessionTimerService.subscribe() (not the inner Observable's
      // .subscribe) so the service knows to start/stop its 1Hz tick based
      // on subscriber count.
      this.sessionTimerSubscription = this.sessionTimerService.subscribe((seconds) => {
        this.secondsSinceSessionStart = seconds;
      });

      this.topicInducedSubscription = this.eventShareService.topicInduced$.subscribe(
        (topic) => {
          this.current_topic = topic;
          this.updateTopics();
          this.fetchTaskStatus();
        }
      )
      
      rolesService.getRoles().subscribe((roles) => {
        this.roles = roles.roles;
      });
    }

  @Input() set currentPageName(pageName: string){
    this._currentPageName = pageName
    this.updateDisplayElements()
  }

  updateDisplayElements(){
    if(this._currentPageName == "tutoringView"){
      this.display_elements.add("taskSelection");
      this.display_elements.add("courseSettings");
      if (this.course_topics.length > 0){
        this.display_elements.add("topicSelection");
      }
    }
    setTimeout(() => {}, 0);
  }

  updateTopics(){
    const curriculum: any = this.course.curriculum
    if (this.course.topics == undefined) {
      this.course_topics = []
    }
    else {
      this.course_topics = this.course.topics
      this.current_topic = sessionStorage.getItem("currentTopic")!;
      this.current_topic_index = this.course_topics.findIndex((topic) => topic === this.current_topic) + 1;
    }
  }

  topicSelected(topic: string){
    console.log(topic);
    this.eventShareService.emitTopicSelected(topic);
    this.current_topic = topic;
    this.fetchTaskStatus();
  }

  fetchTaskStatus(){
    if (this.course && this.current_topic) {
      this.taskStatusService.getTaskStatus(this.course.unique_name, this.current_topic)
        .subscribe({
          next: (data) => {
            this.local_curriculum = data.local_curriculum;
            this.task_status_dict = data.task_status_dict;
            this.computeVisibleBubbles();
          },
          error: (err) => console.error('Failed to fetch task status:', err)
        });
    }
  }

  computeVisibleBubbles(){
    const maxBubbles = 12;
    if (this.local_curriculum.length <= maxBubbles) {
      this.visibleBubbles = [...this.local_curriculum];
      this.showLeftEllipsis = false;
      this.showRightEllipsis = false;
      return;
    }

    const currentIndex = this.local_curriculum.indexOf(this.task_name);
    const halfWindow = Math.floor(maxBubbles / 2);

    let start = currentIndex - halfWindow;
    let end = start + maxBubbles;

    if (start < 0) {
      start = 0;
      end = maxBubbles;
    }

    if (end > this.local_curriculum.length) {
      end = this.local_curriculum.length;
      start = end - maxBubbles;
    }

    this.visibleBubbles = this.local_curriculum.slice(start, end);
    this.showLeftEllipsis = start > 0;
    this.showRightEllipsis = end < this.local_curriculum.length;
  }

  onBubbleClick(taskName: string) {
    if (taskName === this.task_name) {
      return;
    }
    // Allow jumping *backwards* to a previously visited task at any time,
    // but only allow skipping *forward* past the current task once the
    // 5-minute no-skip window has elapsed.
    const localCurriculum = this.local_curriculum || [];
    const currentIndex = localCurriculum.indexOf(this.task_name);
    const targetIndex = localCurriculum.indexOf(taskName);
    const isForwardSkip = currentIndex !== -1 && targetIndex !== -1 && targetIndex > currentIndex;
    if (isForwardSkip && !this.isNextTaskUnlocked()) {
      return;
    }
    this.eventShareService.emitTaskDirectlySelected(taskName);
  }

  ngOnInit() {
    this.show_profile();
  }

  show_profile() {
    this.httpClient.get<any>(`${this.apiUrl}/users/me`, {"withCredentials": true}).subscribe(
      (data)  => {
        this.user_name = data.email!.split("@")[0];
    });
  }

  newTaskButtonClicked(direction: string){
    if (direction === 'next' && !this.isNextTaskUnlocked()) {
      // Defensive: even if the disabled state is bypassed (e.g. via the
      // bubble navigation), keep the 5-minute no-skip window in effect.
      return;
    }
    this.eventShareService.emitNewTaskEvent(direction);
  }

  /**
   * Move to the next task bypassing the 5-minute no-skip lock. Triggered
   * by the secret keyboard shortcut (Ctrl+Shift+Q) so that anyone who
   * knows the shortcut can advance without waiting. The shortcut is
   * deliberately undocumented in the UI; this is the only path the user
   * is asking us to provide.
   */
  private skipToNextTaskUnlocked(): void {
    this.studyTelemetryService.logContextEvent('secret-skip-shortcut', {
      secondsSinceSessionStart: this.secondsSinceSessionStart,
      fromTask: this.task_name,
    });
    this.eventShareService.emitNewTaskEvent('next');
  }

  /**
   * Global keyboard listener for the secret session-advance shortcut.
   *
   * Ctrl+Shift+Q (or Cmd+Shift+Q on macOS) advances the learner to the
   * next task immediately, bypassing the 5-minute no-skip window that
   * the visible Next Task button is gated by. The shortcut is not
   * surfaced anywhere in the UI; it is a hidden affordance for moving
   * through sessions without waiting.
   *
   * The listener is intentionally on `document` (via the component's
   * HostListener) so it fires regardless of which element on the page
   * has focus. We also call `event.preventDefault()` so the browser does
   * not interpret the chord as anything else.
   */
  @HostListener('document:keydown', ['$event'])
  handleGlobalKeydown(event: KeyboardEvent): void {
    if (!event) {
      return;
    }
    const usesModifier = event.ctrlKey || event.metaKey;
    const usesShift = event.shiftKey;
    if (!usesModifier || !usesShift) {
      return;
    }
    const key = (event.key || '').toLowerCase();
    if (key !== 'q') {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    this.skipToNextTaskUnlocked();
  }

  /**
   * True once at least 5 minutes have passed since the session started.
   * While false, the Next Task button is hidden in the toolbar so a
   * learner has a chance to work through the task before being able to
   * skip it.
   */
  isNextTaskUnlocked(): boolean {
    return this.secondsSinceSessionStart >= NavigationBarComponent.NEXT_TASK_UNLOCK_SECONDS;
  }

  /**
   * Remaining seconds until the Next Task button unlocks, or 0 if it is
   * already unlocked. Used for the tooltip countdown.
   */
  nextTaskUnlockCountdown(): number {
    return Math.max(0, NavigationBarComponent.NEXT_TASK_UNLOCK_SECONDS - this.secondsSinceSessionStart);
  }

  /**
   * Human-readable tooltip for the Next Task button. The first 5 minutes of
   * a session it explains the no-skip rule; afterwards it falls back to
   * the standard "Next task" hint.
   */
  nextTaskTooltip(): string {
    if (!this.isNextTaskUnlocked()) {
      const seconds = this.nextTaskUnlockCountdown();
      const minutes = Math.floor(seconds / 60);
      const remainder = seconds % 60;
      const mm = String(minutes).padStart(2, '0');
      const ss = String(remainder).padStart(2, '0');
      return `Next task unlocks in ${mm}:${ss} — take a moment to try before skipping.`;
    }
    return 'Next task';
  }

  emitProfileButtonClicked() {
    this.profileButtonClicked.emit("profileRequest")
  }

  emitHomeButtonClicked() {
    this.homeButtonClicked.emit("homeRequest")
  }

  openAboutPopup() {
    this.markdownDialogService.openAbout();
  }

  openImprintPopup() {
    this.markdownDialogService.openImprint();
  }

  openPrivacyPolicyPopup() {
    this.markdownDialogService.openPrivacyPolicy();
  }

  openHelp() {
    this.helpDialogService.open();
  }

  emitCourseSettingsRequested() {
    this.settingButtonClicked.emit("courseSettingsRequest")
  }

  emitAdminSettingsRequested(){
    this.settingButtonClicked.emit("adminSettingsRequest")
  }

  emitSkillOverviewRequested(){
    this.settingButtonClicked.emit("skillOverviewRequest")
  }

  ngOnDestroy(){
    this.taskFetchedSubscription?.unsubscribe();
    this.topicInducedSubscription?.unsubscribe();
    this.sessionTimerSubscription?.unsubscribe();
  }

}
