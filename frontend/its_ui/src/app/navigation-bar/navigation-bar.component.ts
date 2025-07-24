import { Component, ElementRef, EventEmitter, Output, ViewChild, Input } from '@angular/core';
import { EventShareService } from '../shared/services/event-share.service';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { RolesService } from '../shared/services/roles.service';
import { CourseSettingsService } from '../shared/services/course-settings-service.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.css']
})
export class NavigationBarComponent {

  @Output() profileButtonClicked: EventEmitter<string> = new EventEmitter<string>;
  @Output() homeButtonClicked: EventEmitter<string> = new EventEmitter<string>;
  @Output() settingButtonClicked: EventEmitter<string> = new EventEmitter<string>;

  @ViewChild('aboutPopup', {static: true}) aboutPopup!: ElementRef<HTMLDialogElement>;
  @ViewChild('imprintPopup', {static: true}) imprintPopup!: ElementRef<HTMLDialogElement>;
  @ViewChild('privacyPolicyPopup', {static: true}) privacyPolicyPopup!: ElementRef<HTMLDialogElement>;

  taskFetchedSubscription: Subscription;
  topicInducedSubscription: Subscription;

  aboutMarkdown: string = '';
  imprintMarkdown: string = '';
  privacyPolicyMarkdown: string = '';

  apiUrl: string = environment.apiUrl;
  user_name: string = "INVALID_EMAIL";
  title: string = 'SCRIPT'//'Tutoring System for Programming';
  task_name: string = '';
  course?: any;
  course_topics: string[] = [];
  current_topic: string = "";
  current_topic_index: number = 0;

  roles: string[] = [];

  display_elements: Set<string> = new Set(); 
  _currentPageName?: string

  constructor(
    private eventShareService: EventShareService,
    private httpClient: HttpClient,
    private rolesService: RolesService,
    private courseSettingsService: CourseSettingsService
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
              });
          }
        });

      this.topicInducedSubscription = this.eventShareService.topicInduced$.subscribe(
        (topic) => {
          this.current_topic = topic;
          this.updateTopics();
        }
      )
      
      rolesService.getRoles().subscribe((roles) => {
        this.roles = roles.roles;
      });
      //this.roles = sessionStorage.getItem("roles")!.split(",")
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
  }

  ngAfterViewInit() {
    this.show_profile()
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
    //this.eventShareService.emitProfileButtonClick();
    this.profileButtonClicked.emit("profileRequest")
  }

  emitHomeButtonClicked() {
    //this.eventShareService.emitProfileButtonClick();
    this.homeButtonClicked.emit("homeRequest")
  }

  openAboutPopup() {
    this.httpClient.get<any>(`${environment.apiUrl}/info/about`)
        .subscribe(data => {
          this.aboutMarkdown = data.about_markdown;
        });
    this.aboutPopup.nativeElement.showModal();
  }
  openImprintPopup() {
    this.httpClient.get<any>(`${environment.apiUrl}/info/imprint`)
        .subscribe(data => {
          this.aboutMarkdown = data.imprint_markdown;
        });
        console.log('bloody hell')
    this.aboutPopup.nativeElement.showModal();
  }

  openPrivacyPolicyPopup() {
    this.httpClient.get<any>(`${environment.apiUrl}/info/privacy_policy`)
        .subscribe(data => {
          this.privacyPolicyMarkdown = data.privacy_policy_markdown;
        });
    this.privacyPolicyPopup.nativeElement.showModal();
  }
  emitCourseSettingsRequested() {
    this.settingButtonClicked.emit("courseSettingsRequest")
  }

  emitAdminSettingsRequested(){
    this.settingButtonClicked.emit("adminSettingsRequest")
  }

  ngOnDestroy(){
    this.taskFetchedSubscription.unsubscribe();
    this.topicInducedSubscription.unsubscribe();
  }

}