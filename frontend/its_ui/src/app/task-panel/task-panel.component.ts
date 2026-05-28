import { Component, ElementRef, ViewChild, Input, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { EventShareService } from '../shared/services/event-share.service';
import { Subscription, delay } from 'rxjs';
import { environment } from 'src/environments/environment';
import { CourseSettingsService } from '../shared/services/course-settings-service.service';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { StudyFunctionsService } from '../shared/services/study-functions.service';
import { StudyTelemetryService } from '../shared/services/study-telemetry.service';

import { MarkdownPanelComponent } from '../shared/components/markdown-panel/markdown-panel.component';

@Component({
    selector: 'app-task-panel',
    templateUrl: './task-panel.component.html',
    styleUrls: ['./task-panel.component.css'],
    imports: [CommonModule, MarkdownPanelComponent, MatTooltipModule, MatIconModule]
})
export class TaskPanelComponent {

  @ViewChild("courseCompleteDialog", { static: true }) courseCompleteDialog!: ElementRef<HTMLDialogElement>;
  @ViewChild(MarkdownPanelComponent) markdownPanelComponent!: MarkdownPanelComponent;
  @Input() initTask?: string | null = null;

  private eventSubscription: Subscription;
  private topicSelectionSubscription: Subscription;
  private taskDirectlySelectedSubscription: Subscription;
  task_markdown: string = '';
  code_language: string = 'python';

  //@Input() course: {unique_name?: string; curriculum?: string[]} = {}
  course: { unique_name?: string; curriculum?: string[] | any, topics?: string[], default_topic?: string } = {}
  task: {
    unique_name?: string; task?: string; type?: string, prefix?: string,
    arguments?: string[], possible_choices?: string, feedback_available?: string
  } = {};
  current_topic: string = "";
  sessionCompletionPending: boolean = false;
  sessionDownloadUrl: string | null = null;
  sessionSurveyUrl: string | null = null;
  sessionPreviewUrl: string | null = null;
  sessionCompletionError: string | null = null;

  constructor(
    private client: HttpClient,
    private eventShareService: EventShareService,
    private courseSettingsService: CourseSettingsService,
    public studyFunctionsService: StudyFunctionsService,
    private studyTelemetryService: StudyTelemetryService,
  ) {
    this.eventSubscription = this.eventShareService.newTaskEvent$.subscribe((message) => {
      this.selectAndFetchTask(message);
    });
    this.topicSelectionSubscription = this.eventShareService.topicSelected$.subscribe((topic) => {
      this.current_topic = topic;
      sessionStorage.setItem("currentTopic", topic);
      this.selectAndFetchTask("personal");
    })
    this.taskDirectlySelectedSubscription = this.eventShareService.taskDirectlySelected$.subscribe((taskName) => {
      this.fetch_task(taskName);
    })
  }

  selectAndFetchTask(message: string) {
    console.log(message)
    var localCurriculum: string[] = this.getLocalCurriculum();
    const current_task_name = this.task.unique_name!;
    const task_index: number = localCurriculum.findIndex((element) => element == current_task_name);
    if (message == 'next') {
      if (task_index == (localCurriculum.length - 1)) {
        if (this.course.topics != undefined) {
          const topicIndex = this.course.topics.findIndex((element) => element == this.current_topic)
          if (topicIndex < this.course.topics.length - 1) {
            this.current_topic = this.course.topics[topicIndex + 1];
            this.eventShareService.emitTopicInduced(this.current_topic);
            sessionStorage.setItem("currentTopic", this.current_topic);
            localCurriculum = this.getLocalCurriculum()
            this.fetch_task(localCurriculum[0]);
            return
          }
          else {
            alert("No further tasks available")
            return;
          }
        }
        else {
          alert("No further task availiable.")
          return;
        }
      }
      this.fetch_task(localCurriculum[task_index + 1]);
    }
    if (message == 'previous') {
      if (task_index == 0) {
        if (this.course.topics != undefined) {
          const topicIndex = this.course.topics.findIndex((element) => element == this.current_topic)
          if (topicIndex != 0) {
            this.current_topic = this.course.topics[topicIndex - 1];
            this.eventShareService.emitTopicInduced(this.current_topic);
            sessionStorage.setItem("currentTopic", this.current_topic);
            localCurriculum = this.getLocalCurriculum()
            this.fetch_task(localCurriculum[localCurriculum.length - 1]);
            return
          }
        }
        else {
          alert("Previous Task doesn't exist");
          return;
        }
      }
      this.fetch_task(localCurriculum[task_index - 1]);
    }
    if (message == 'personal') {
      if (this.isLivePreviewMode()) {
        this.fetchLivePreviewTask();
        return;
      }
      if (this.current_topic != undefined) {
        this.fetch_task(undefined, this.current_topic);
      }
      else {
        this.fetch_task();
      }
    }
  }

  getLocalCurriculum() {
    this.ensureCurrentTopic();
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

  private ensureCurrentTopic(): void {
    if (this.course.topics != undefined && !this.current_topic) {
      this.current_topic = this.course.default_topic || this.course.topics[0] || "";
      if (this.current_topic) {
        sessionStorage.setItem("currentTopic", this.current_topic);
      }
    }
  }

  private isLivePreviewMode(): boolean {
    return sessionStorage.getItem('livePreviewMode') === 'true';
  }

  private fetchLivePreviewTask(): void {
    const nextTask = this.resolveLivePreviewTask();
    if (!nextTask || nextTask === 'course completed') {
      this.handleCourseCompleted();
      return;
    }

    this.fetch_task(nextTask, this.current_topic);
  }

  private resolveLivePreviewTask(): string {
    let localCurriculum = this.getLocalCurriculum();
    if (localCurriculum.length === 0) {
      return 'course completed';
    }

    const currentTaskName = this.task.unique_name;
    if (!currentTaskName || currentTaskName === 'course completed') {
      return localCurriculum[0];
    }

    const taskIndex = localCurriculum.findIndex((element) => element == currentTaskName);
    if (taskIndex === -1) {
      return localCurriculum[0];
    }

    if (taskIndex < localCurriculum.length - 1) {
      return localCurriculum[taskIndex + 1];
    }

    if (this.course.topics != undefined) {
      const topicIndex = this.course.topics.findIndex((element) => element == this.current_topic);
      if (topicIndex >= 0 && topicIndex < this.course.topics.length - 1) {
        this.current_topic = this.course.topics[topicIndex + 1];
        this.eventShareService.emitTopicInduced(this.current_topic);
        sessionStorage.setItem("currentTopic", this.current_topic);
        localCurriculum = this.getLocalCurriculum();
        return localCurriculum[0] || 'course completed';
      }
    }

    return 'course completed';
  }

  private handleCourseCompleted(): void {
    this.studyTelemetryService.logContextEvent('course-completed', {
      topic: this.current_topic || null,
    });
    this.sessionDownloadUrl = null;
    this.sessionSurveyUrl = null;
    this.sessionPreviewUrl = null;
    this.sessionCompletionError = null;
    this.eventShareService.emitViewChange('finalShowcase');
  }

  fetch_task(task_unique_name?: string, topic?: string) {
    var task_url: string;
    if (typeof task_unique_name == 'undefined') {
      task_url = `${environment.apiUrl}/task/for_user/`;
      if (topic != undefined) {
        task_url = task_url + `${topic}`
      }
    }
    else {
      task_url = `${environment.apiUrl}/task/by_name/${task_unique_name}`;
    }
    this.client.get<any>(task_url, { withCredentials: true }).subscribe(
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
          this.handleCourseCompleted();
          return;
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
        sessionStorage.setItem("additionalFiles", JSON.stringify(data.additional_files || []));
        this.studyTelemetryService.logContextEvent('task-opened', {
          taskLength: this.task['task']?.length || 0,
          hasArguments: Array.isArray(this.task['arguments']) && this.task['arguments'].length > 0,
          additionalFilesCount: Array.isArray(data.additional_files) ? data.additional_files.length : 0,
        });
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

  ngAfterViewInit() {
    this.courseSettingsService.getCourse().subscribe((course) => {
      this.course = course;
      if (this.course.default_topic != undefined) {
        this.current_topic = this.course.default_topic!;
        sessionStorage.setItem("currentTopic", this.current_topic!);
      }
      if (this.initTask == null) {
        this.selectAndFetchTask("personal");
      }
      else {
        this.fetch_task(this.initTask, this.current_topic);
      }
    });
  }

  ngOnDestroy() {
    this.eventSubscription.unsubscribe();
    this.topicSelectionSubscription.unsubscribe();
    this.taskDirectlySelectedSubscription.unsubscribe();
  }

  async completeStudySession(): Promise<void> {
    if (!this.studyFunctionsService.isConfigured || this.sessionCompletionPending) {
      return;
    }

    this.sessionCompletionPending = true;
    this.sessionCompletionError = null;

    try {
      const latestCode = sessionStorage.getItem('latestCode') || '';
      const response = await this.studyFunctionsService.completeCurrentSession(latestCode);
      this.sessionDownloadUrl = this.studyFunctionsService.getDownloadUrl(response.fileId);
      this.sessionSurveyUrl = response.surveyUrl;
      this.client.post<any>(
        `${environment.apiUrl}/info/final_preview_link`,
        { code: latestCode, title: 'Final App Preview' },
        { withCredentials: true }
      ).subscribe({
        next: (previewResponse) => {
          this.sessionPreviewUrl = previewResponse.preview_url;
        },
        error: () => {
          this.sessionPreviewUrl = null;
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

}
