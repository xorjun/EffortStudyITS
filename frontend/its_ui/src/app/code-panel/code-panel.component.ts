import { Component, Renderer2,  AfterViewChecked, AfterViewInit, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { DatePipe } from '@angular/common';

//Prism
import { fromEvent, Subscription, timeout } from 'rxjs';
import { HttpClient } from '@angular/common/http';

import { EventShareService } from '../shared/services/event-share.service';
import { CodeEditorComponent } from './code-editor/code-editor.component';
import { DatetimeService } from '../shared/services/datetime.service';

import { environment } from 'src/environments/environment';
import { MultipleChoiceComponent } from './multiple-choice/multiple-choice.component';


@Component({
  selector: 'app-code-panel',
  templateUrl: './code-panel.component.html',
  styleUrls: ['./code-panel.component.css'],
})
export class CodePanelComponent {

  submitted_code: string = ''
  code_language = 'python';

  //TODO: the editor is initialized and listens for changes even for MC-Questions.
  @ViewChild(CodeEditorComponent)
  codeEditorComponent!: CodeEditorComponent;
  lastSavedCode!: string;

  @ViewChild(MultipleChoiceComponent)
  multipleChoiceComponent!: MultipleChoiceComponent;
  isMultipleChoice: boolean = false;

  feedbackAvailable!: boolean;

  //Submit Button
  submitButtonClicked() {
    var payload = {}
    if(this.isMultipleChoice) {
      payload = {
        selected_choices: this.multipleChoiceComponent.checked,
        task_unique_name: this.current_task_id, 
        course_unique_name: sessionStorage.getItem("courseID"),
        code: "",
        log: "True", 
        type: "submission",
        submission_time: this.datetimeService.datetimeNow()
      }
    }
    else {
      this.submitted_code = this.codeEditorComponent.userContentControl;
      payload = {task_unique_name: this.current_task_id, code: this.submitted_code, 
        course_unique_name: sessionStorage.getItem("courseID"),
        log: "True", 
        type: "submission",
        selected_choices: [],
        submission_time: this.datetimeService.datetimeNow()
      }

    }
    // TODO fix: sometimes this.codeEditorComponent is undefinded
    this.client.post<any>(`${environment.apiUrl}/submit`, payload, {withCredentials: true}).subscribe((data) => {
      if (!this.isMultipleChoice) {
        this.codeEditorComponent.appendContent([[-2, data.submission_id]]);
      }
      this.eventShareService.emitTestReadyEvent(data.submission_id);
    })
  }

  //Run Button
  handleRunEvent(parameters: any) {
    var runCode = this.codeEditorComponent.userContentControl;
    const body = {task_unique_name: this.current_task_id,
                course_unique_name: sessionStorage.getItem("courseID"),
                code: runCode,
                log: "True", 
                selected_choices: [],
                submission_time: this.datetimeService.datetimeNow(),
                run_arguments: parameters, type: "run"};
    this.client.post<any>(`${environment.apiUrl}/run/run_code`, body, {withCredentials: true}).subscribe(
      (data) => {
        this.codeEditorComponent.appendContent([[-2, data.run_id]])
        this.eventShareService.emitCodeRunReadyEvent(data.run_id);
      }
    );
  }

  taskFetchedSubscription?: Subscription;
  current_task_id: string = "";

  constructor(
      private client: HttpClient,
      private eventShareService: EventShareService,
      public datePipe: DatePipe,
      private datetimeService: DatetimeService,
    ) {

  }

  ngAfterViewInit(){
    this.taskFetchedSubscription = this.eventShareService.newTaskFetched$.subscribe((data) => {
      this.isMultipleChoice = sessionStorage.getItem("taskType")! == "multiple_choice";
      setTimeout(() => {
        this.current_task_id = sessionStorage.getItem("taskId")!;
        this.feedbackAvailable = sessionStorage.getItem("feedbackAvailable") == "true";
        if (sessionStorage.getItem("taskType")! != "multiple_choice"){
          if(this.codeEditorComponent.contentControl != this.lastSavedCode) {
          this.recordChanges(this.codeEditorComponent.newContentList);
          this.codeEditorComponent.newContentList = [];
          }
        }
        if (!this.isMultipleChoice){
          this.codeEditorComponent.prefix = sessionStorage.getItem("taskPrefix")!;
        }
        this.getCurrentAttemptState();
      }, 0); // 0 timeout to let DOM load first.
      })
  }

    // Tracking Users Coding process, also functionality to save and restore attempts.

    currentAttemptId!: string;
    contentReloaded: boolean = false;

    getCurrentAttemptState() {
      this.client.get<any>(`${environment.apiUrl}/attempt/get_state/${this.current_task_id}`, {withCredentials: true}).subscribe(
        (data) => {
          this.currentAttemptId = data.attempt_id;
          if(this.isMultipleChoice) {
            let choices = JSON.parse(sessionStorage.getItem('taskChoices')!);
            this.multipleChoiceComponent.choices = choices;
          }
          else {
            //this.codeEditorComponent.form.setValue({'content': sessionStorage.getItem('taskPrefix') + data.code});
            this.codeEditorComponent.setEditorContent(sessionStorage.getItem('taskPrefix') + data.code);
            this.codeEditorComponent.lastSnapshot = data.code;
          }
          this.contentReloaded = true;
          this.lastSavedCode = data.code;
        }
      )
    }

    recordChanges(newContentList: string[]) {
      /* newContent = this.codeEditorComponent.userContentControl; */
      const prefix = sessionStorage.getItem("taskPrefix")!;
      //if (newContentList.startsWith(prefix)) {
      //  newContent = newContent.slice(prefix.length);
      //} 
/*       if (newContentList.length == 0){
        return;
      } */
      if ((!this.contentReloaded) || (this.current_task_id=='course completed')) {
        //ensure that code has changed
        if((this.lastSavedCode == newContentList[newContentList.length-1])) {
          return;};
        const body = {
          'attempt_id': this.currentAttemptId,
          'code_list': newContentList, 
          'state_datetime_list': this.codeEditorComponent.datetimeList,
          'dataCollection': sessionStorage.getItem('dataCollection'),
          'current_state': this.codeEditorComponent.lastSnapshot
        }
        this.client.post<any>(`${environment.apiUrl}/attempt/log`, body, {withCredentials: true}).subscribe(
          () => {
            console.log("State saved");
          }
        )
      }
        this.contentReloaded = false;
        this.lastSavedCode = newContentList[newContentList.length-1];
    }

    handleFeedbackEvent() {
      console.log("Feedback requested")
      if(!this.isMultipleChoice) {
        this.submitted_code = this.codeEditorComponent.userContentControl;
        this.client.post<any>(`${environment.apiUrl}/feedback`, 
          {
            // TODO: Do we need to include selected choices since MC is excluded?
            selected_choices: [],
            task_unique_name: this.current_task_id, 
            course_unique_name: sessionStorage.getItem("courseID"),
            code: this.submitted_code,
            log: "True", 
            type: "feedback_request",
            submission_time: this.datetimeService.datetimeNow()
          },
          {withCredentials: true}).subscribe((data) => {
            this.eventShareService.emitFeedbackReadyEvent(data.feedback_id);
          }
        );
      }
    }

    ngOnDestroy(){
    if(this.codeEditorComponent != undefined && this.codeEditorComponent.contentControl != this.lastSavedCode) {
      this.recordChanges(this.codeEditorComponent.newContentList);
    }
    this.taskFetchedSubscription?.unsubscribe();
   }
}
