import { Component } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { EventShareService } from '../shared/services/event-share.service';
import { DatetimeService } from '../shared/services/datetime.service';
import { environment } from 'src/environments/environment';
import { CodeEditorComponent } from './code-editor/code-editor.component';
import { MultipleChoiceComponent } from './multiple-choice/multiple-choice.component';
import { ActionPanelComponent } from './action-panel/action-panel.component';
import { ViewChild, AfterViewInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { StudyFunctionsService } from '../shared/services/study-functions.service';
import { StudyTelemetryService } from '../shared/services/study-telemetry.service';
import { StudyBannerService } from '../shared/services/study-banner.service';

@Component({
    selector: 'app-code-panel',
    templateUrl: './code-panel.component.html',
    styleUrls: ['./code-panel.component.css'],
    imports: [CommonModule, CodeEditorComponent, MultipleChoiceComponent, ActionPanelComponent]
})
export class CodePanelComponent implements AfterViewInit, OnDestroy {

  submitted_code: string = ''
  code_language = 'python';
  disableEditorCopyPaste: boolean = false;

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
      sessionStorage.setItem('latestCode', this.submitted_code);
      payload = {task_unique_name: this.current_task_id, code: this.submitted_code, 
        course_unique_name: sessionStorage.getItem("courseID"),
        log: "True", 
        type: "submission",
        selected_choices: [],
        submission_time: this.datetimeService.datetimeNow()
      }

    }
    this.studyTelemetryService.logContextEvent('submission-request', {
      attemptId: this.currentAttemptId,
      multipleChoice: this.isMultipleChoice,
      codeLength: this.isMultipleChoice ? 0 : this.submitted_code.length,
      selectedChoiceCount: this.isMultipleChoice ? this.multipleChoiceComponent.checked.length : 0,
    });
    // TODO fix: sometimes this.codeEditorComponent is undefinded
    this.client.post<any>(`${environment.apiUrl}/submit`, payload, {withCredentials: true}).subscribe((data) => {
      this.studyTelemetryService.logContextEvent('submission-created', {
        attemptId: this.currentAttemptId,
        submissionId: data.submission_id,
      });
      if (!this.isMultipleChoice) {
        this.codeEditorComponent.appendContent([[-2, data.submission_id]]);
      }
      this.eventShareService.emitTestReadyEvent(data.submission_id);
    })
  }

  //Run Button
  handleRunEvent(eventData: { parameters: any, showConsoleOutput: boolean }) {
    this.studyBannerService.registerEvent('code-run');
    var runCode = this.codeEditorComponent.userContentControl;
    sessionStorage.setItem('latestCode', runCode);
    // Always show console output for plotting tasks
    const isPlottingTask = sessionStorage.getItem("taskType") === "plot_function";
    const showConsoleOutput = isPlottingTask ? true : eventData.showConsoleOutput;
    this.studyTelemetryService.logContextEvent('run-request', {
      attemptId: this.currentAttemptId,
      parameters: eventData.parameters,
      codeLength: runCode.length,
      showConsoleOutput,
      isPlottingTask,
    });
    const body = {task_unique_name: this.current_task_id,
                course_unique_name: sessionStorage.getItem("courseID"),
                code: runCode,
                log: "True",
                selected_choices: [],
                submission_time: this.datetimeService.datetimeNow(),
                run_arguments: eventData.parameters,
                show_console_output: showConsoleOutput,
                type: "run"};
    this.client.post<any>(`${environment.apiUrl}/run/run_code`, body, {withCredentials: true}).subscribe(
      (data) => {
        this.studyTelemetryService.logContextEvent('run-created', {
          attemptId: this.currentAttemptId,
          runId: data.run_id,
        });
        this.codeEditorComponent.appendContent([[-2, data.run_id]])
        this.eventShareService.emitCodeRunReadyEvent(data.run_id);
        if (data.stderr || data.compile_output || data.status === 'error') {
          this.studyBannerService.registerEvent('error');
        }
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
      private studyFunctionsService: StudyFunctionsService,
      private studyTelemetryService: StudyTelemetryService,
      private studyBannerService: StudyBannerService,
    ) {

  }

  ngAfterViewInit(){
    this.loadEditorPolicy();
    void this.studyFunctionsService.ensureActiveSession();
    this.studyBannerService.markSessionStarted();
    this.taskFetchedSubscription = this.eventShareService.newTaskFetched$.subscribe((data) => {
      this.loadEditorPolicy();
      void this.studyFunctionsService.ensureActiveSession();
      this.studyBannerService.markSessionStarted();
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
          this.codeEditorComponent.setAdditionalFiles(sessionStorage.getItem("additionalFiles"));
          this.codeEditorComponent.resetForNewTask();
        }
        this.getCurrentAttemptState();
      }, 0); // 0 timeout to let DOM load first.
      })
  }

    loadEditorPolicy() {
      this.client.get<{ disable_editor_copy_paste: boolean }>(`${environment.apiUrl}/settings/editor_policy`).subscribe({
        next: (data) => {
          this.disableEditorCopyPaste = !!data.disable_editor_copy_paste;
        },
        error: () => {
          this.disableEditorCopyPaste = false;
        }
      });
    }

    handleClipboardTelemetryEvent(eventData: { action: string, blocked: boolean }) {
      this.studyTelemetryService.logContextEvent('clipboard', {
        ...eventData,
        attemptId: this.currentAttemptId,
      });
      if (!this.currentAttemptId || this.current_task_id === 'course completed') {
        return;
      }
      this.client.post<any>(
        `${environment.apiUrl}/attempt/clipboard_event`,
        {
          attempt_id: this.currentAttemptId,
          action: eventData.action,
          blocked: eventData.blocked,
          event_datetime: this.datetimeService.datetimeNow(),
        },
        { withCredentials: true }
      ).subscribe({
        error: () => {}
      });
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
          this.studyTelemetryService.logContextEvent('attempt-session-open', {
            attemptId: data.attempt_id,
            restoredCodeLength: typeof data.code === 'string' ? data.code.length : 0,
            multipleChoice: this.isMultipleChoice,
          });
        }
      )
    }

    recordChanges(newContentList: string[]) {
      if (newContentList.length === 0) {
        return;
      }
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
            this.studyTelemetryService.logContextEvent('attempt-state-saved', {
              attemptId: this.currentAttemptId,
              snapshotCount: newContentList.length,
              snapshotTimestamps: this.codeEditorComponent.datetimeList.slice(-newContentList.length),
              currentStateLength: this.codeEditorComponent.lastSnapshot.length,
              currentStatePreview: this.codeEditorComponent.lastSnapshot.slice(0, 3000),
            });
            console.log("State saved");
          }
        )
      }
        this.contentReloaded = false;
        this.lastSavedCode = newContentList[newContentList.length-1];
        this.studyFunctionsService.scheduleAutosave(this.codeEditorComponent.userContentControl);
    }

    handleFeedbackEvent() {
      console.log("Feedback requested")
      this.studyTelemetryService.logContextEvent('hint-open', {
        attemptId: this.currentAttemptId,
        codeLength: this.isMultipleChoice ? 0 : this.codeEditorComponent.userContentControl.length,
      });
      this.studyBannerService.registerEvent('hint-open');
      if(!this.isMultipleChoice) {
        this.submitted_code = this.codeEditorComponent.userContentControl;
        sessionStorage.setItem('latestCode', this.submitted_code);
        if (this.studyFunctionsService.canUseAiAssistance()) {
          void this.studyFunctionsService.requestAiHint(
            `Task ${this.current_task_id}: provide the next best hint based on the learner's current code.`,
            this.submitted_code,
          ).then((response) => {
            this.studyTelemetryService.logContextEvent('ai-query', {
              attemptId: this.currentAttemptId,
              remainingQueries: response.remainingQueries,
              tokensUsed: response.tokensUsed,
              responseLength: response.responseText.length,
              source: 'appwrite',
            });
            this.eventShareService.emitExternalFeedback({
              markdown: response.responseText,
              source: 'appwrite-ai',
              feedbackId: 'appwrite-ai',
            });
          }).catch(() => {
            this.requestLegacyFeedback();
          });
          return;
        }
        this.requestLegacyFeedback();
      }
    }

    private requestLegacyFeedback() {
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
          {withCredentials: true}).subscribe({
            next: (data) => {
              if (!data?.feedback_id) {
                this.eventShareService.emitExternalFeedback({
                  markdown: 'Feedback is currently unavailable. Please try again in a moment.',
                  source: 'legacy-error',
                });
                return;
              }
              this.studyTelemetryService.logContextEvent('feedback-request', {
                attemptId: this.currentAttemptId,
                feedbackId: data.feedback_id,
                source: 'legacy',
                codeLength: this.submitted_code.length,
              });
              this.eventShareService.emitFeedbackReadyEvent(data.feedback_id);
            },
            error: () => {
              this.eventShareService.emitExternalFeedback({
                markdown: 'Feedback is currently unavailable. Please try again in a moment.',
                source: 'legacy-error',
              });
            }
          }
        );
    }

    ngOnDestroy(){
    if(this.codeEditorComponent != undefined && this.codeEditorComponent.contentControl != this.lastSavedCode) {
      this.recordChanges(this.codeEditorComponent.newContentList);
    }
    this.taskFetchedSubscription?.unsubscribe();
   }
}
