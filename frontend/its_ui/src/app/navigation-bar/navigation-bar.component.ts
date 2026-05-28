import { Component, EventEmitter, Output, Input } from '@angular/core';
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

  constructor(
    private eventShareService: EventShareService,
    private httpClient: HttpClient,
    private rolesService: RolesService,
    private courseSettingsService: CourseSettingsService,
    private markdownDialogService: MarkdownDialogService,
    private taskStatusService: TaskStatusService
    ){
      this.taskFetchedSubscription = this.eventShareService.newTaskFetched$.subscribe(
        () => {
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
    if (taskName !== this.task_name) {
      this.eventShareService.emitTaskDirectlySelected(taskName);
    }
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
    this.eventShareService.emitNewTaskEvent(direction);
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
    this.taskFetchedSubscription.unsubscribe();
    this.topicInducedSubscription.unsubscribe();
  }

}
