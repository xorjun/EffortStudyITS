import { Component, ElementRef, ViewChild, Input, AfterViewInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EventShareService } from '../shared/services/event-share.service';
import { Subscription, delay } from 'rxjs';
import { environment } from 'src/environments/environment';
import { CourseSettingsService } from '../shared/services/course-settings-service.service';

import { MarkdownPanelComponent } from '../shared/components/markdown-panel/markdown-panel.component';

@Component({
  selector: 'app-task-panel',
  templateUrl: './task-panel.component.html',
  styleUrls: ['./task-panel.component.css']
})
export class TaskPanelComponent {

  @ViewChild("courseCompleteDialog", {static: true}) courseCompleteDialog!: ElementRef<HTMLDialogElement>;
  @ViewChild(MarkdownPanelComponent) markdownPanelComponent!: MarkdownPanelComponent;
  @Input() initTask?: string | null = null;

  private eventSubscription: Subscription;
  private topicSelectionSubscription: Subscription;
  task_markdown: string = '';
  code_language: string = 'python';

  //@Input() course: {unique_name?: string; curriculum?: string[]} = {}
  course: {unique_name?: string; curriculum?: string[] | any, topics?: string[], default_topic?: string} = {}
  task: {unique_name?: string; task?: string; type?: string, prefix?: string, 
    arguments?: string[], possible_choices?: string, feedback_available?: string} = {};
  current_topic: string = "";

  constructor(
    private client: HttpClient,
    private eventShareService: EventShareService,
    private courseSettingsService: CourseSettingsService
    ){
      this.eventSubscription = this.eventShareService.newTaskEvent$.subscribe((message) => {
        this.selectAndFetchTask(message);
      });
      this.topicSelectionSubscription = this.eventShareService.topicSelected$.subscribe((topic) => {
        this.current_topic = topic;
        sessionStorage.setItem("currentTopic", topic);
        this.selectAndFetchTask("personal");
      })
    }

  selectAndFetchTask(message: string) {
    console.log(message)
    var localCurriculum: string[] = this.getLocalCurriculum();
    const current_task_name = this.task.unique_name!;
    const task_index: number = localCurriculum.findIndex((element) => element == current_task_name);
    if (message == 'next') {
      if (task_index == (localCurriculum.length-1)) {
        if (this.course.topics != undefined){
          const topicIndex = this.course.topics.findIndex((element) => element==this.current_topic)
          if (topicIndex < this.course.topics.length -1){
            this.current_topic = this.course.topics[topicIndex + 1];
            this.eventShareService.emitTopicInduced(this.current_topic);
            sessionStorage.setItem("currentTopic", this.current_topic);
            localCurriculum = this.getLocalCurriculum()
            this.fetch_task(localCurriculum[0]);
            return
          }
          else{
            alert("No further tasks available")
            return;
          }
        }
        else{
          alert("No further task availiable.")
          return;
        }
      }
      this.fetch_task(localCurriculum[task_index+1]);
    }
    if (message == 'previous') {
      if (task_index == 0) {
        if (this.course.topics != undefined){
          const topicIndex = this.course.topics.findIndex((element) => element==this.current_topic)
          if (topicIndex != 0){
            this.current_topic = this.course.topics[topicIndex - 1];
            this.eventShareService.emitTopicInduced(this.current_topic);
            sessionStorage.setItem("currentTopic", this.current_topic);
            localCurriculum = this.getLocalCurriculum()
            this.fetch_task(localCurriculum[localCurriculum.length - 1]);
            return
          }
        }
        else{
          alert("Previous Task doesn't exist");
          return;
        }
      }
      this.fetch_task(localCurriculum[task_index-1]);
    }
    if (message == 'personal') {
      if (this.current_topic != undefined) {
        this.fetch_task(undefined, this.current_topic);
      }
      else{
        this.fetch_task();
      }
    }
  }

  getLocalCurriculum(){
    const curriculum = this.course.curriculum!;
    var localCurriculum: string[];
    if (this.course.topics != undefined) {
      localCurriculum = this.course.curriculum[this.current_topic];
    }
    else {
      localCurriculum = curriculum;
    }
    return localCurriculum;
  }

  fetch_task(task_unique_name?: string, topic?: string) {
    var task_url: string;
    if (typeof task_unique_name == 'undefined') {
      task_url = `${environment.apiUrl}/task/for_user/`;
      if (topic != undefined){
        task_url = task_url + `${topic}`
      }
    }
    else {
      task_url = `${environment.apiUrl}/task/by_name/${task_unique_name}`;
    }
    this.client.get<any>(task_url, {withCredentials: true}).subscribe(
      (data) => {
      this.task = {
        unique_name: data.unique_name,
        task: data.task,
        type: data.type,
        prefix: data.prefix,
        arguments: data.arguments,
        possible_choices: data.possible_choices,
        feedback_available: data.feedback_available,
    };
    
    console.log("new task request")
    if (this.task['unique_name'] == "course completed") {
      delay(100);
      this.courseCompleteDialog.nativeElement.showModal();
    }
    this.task_markdown = this.task['task']!;
    //console.log(this.task['unique_name'])
    //this.dataShareService.emitTaskId(this.task['unique_name']!);
    
    sessionStorage.setItem("taskId", this.task['unique_name']!);
    sessionStorage.setItem("taskType", this.task['type']!);
    sessionStorage.setItem("taskArguments", JSON.stringify(this.task['arguments']!));
    sessionStorage.setItem("taskPrefix", this.task['prefix']!);
    sessionStorage.setItem("taskChoices", JSON.stringify(this.task['possible_choices']!));
    sessionStorage.setItem("feedbackAvailable", this.task["feedback_available"]!);
    this.markdownPanelComponent.resetScroll();
    this.eventShareService.emitNewTaskFetchedEvent();
  });
 }


 /*updateTopic(taskUniqueName: string){
  if (!this.course.curriculum[this.current_topic].includes(taskUniqueName))
  {
    for (let i = 0; i < this.course.topics!.length; i++) {
      const topic = this.course.topics![i];
      if (this.course.curriculum[this.course.topics![i]].includes(taskUniqueName)){
        this.current_topic = topic

      }
    }
  }
 } */

/*   ngOnInit(): void {
    // Fetch the first task with timeout in order to load the whole app.
    setTimeout(()=>{  
      const courseID = sessionStorage.getItem("courseID")
      this.client.get<any>(`${environment.apiUrl}/course/get/${courseID}`, {withCredentials: true}).subscribe(
        (data) => {
          this.course = {
            unique_name: data.unique_name,
            curriculum: data.curriculum,
          }
        }
      ); 
      console.log(this.initTask);                        
      if (this.initTask == null) {
        this.fetch_task();
      }
      else {
        this.fetch_task(this.initTask);
      }
  }, 300);
  } */

  ngAfterViewInit(){
    this.courseSettingsService.getCourse().subscribe((course) =>
    {
      this.course = course;
      if (this.course.default_topic != undefined) {
        this.current_topic = this.course.default_topic!;
        sessionStorage.setItem("currentTopic", this.current_topic!);
      }
      if (this.initTask == null) {
        this.fetch_task(undefined, this.current_topic);
      }
      else {
        this.fetch_task(this.initTask, this.current_topic);
      }
    });
  }

  ngOnDestroy() {
    this.eventSubscription.unsubscribe();
    this.topicSelectionSubscription.unsubscribe();
  }

}
