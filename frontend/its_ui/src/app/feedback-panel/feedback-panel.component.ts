import { Component, ElementRef, ViewChild } from '@angular/core';
import { Subscription } from 'rxjs';
import { EventShareService } from '../shared/services/event-share.service';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-feedback-panel',
  templateUrl: './feedback-panel.component.html',
  styleUrls: ['./feedback-panel.component.css']
})
export class FeedbackPanelComponent {
  show: boolean = true

  @ViewChild("taskSolvedDialog", {static: true}) taskSolvedDialog!: ElementRef<HTMLDialogElement>;

  private submitSubscription: Subscription;
  private testReadySubscription: Subscription;
  private newTaskSubscription: Subscription;
  private codeRunSubscription: Subscription;
  private codeRunReadySubscription: Subscription;
  private feedbackRequestSubscription: Subscription;
  private feedbackReadySubscription: Subscription;

  code_language: string = 'python';
  feedback_markdown: string = '';
  feedback:  { test_results?: Array<any>; task_id?: string; submission_id?: string; 
    valid_solution?: boolean, output?: boolean, feedback?: string} = {};
  submissionId: string = '';
  displayFeedbackSurvey = false;
  currentFeedbackID: string = "";
  

  constructor(
    private eventShareService: EventShareService,
    private client: HttpClient,){
    //Subscriptions for code submit
    this.submitSubscription = this.eventShareService.submitButtonClick$.subscribe((data) => {
      this.feedback_markdown = 'Code submitted, waiting for feedback...';
      this.displayFeedbackSurvey = false;
    });
    this.testReadySubscription = this.eventShareService.testReady$.subscribe((data) => {
      console.log("data", data)
      this.displayFeedbackSurvey = false;
      const submissionId = data
      this.fetchSubmissionFeedback(submissionId);
    });
    // New Task subscription
    this.newTaskSubscription = this.eventShareService.newTaskEvent$.subscribe(() => {
      this.displayFeedbackSurvey = false;
      this.feedback_markdown = '';
    });
    // Subscriptions for code run
    this.codeRunSubscription = this.eventShareService.runButtonClick$.subscribe(
      () => {
        this.displayFeedbackSurvey = false;
        this.feedback_markdown = 'Code Experiment started, waiting for results...'
      }
    );
    this.codeRunReadySubscription = this.eventShareService.codeRunReady$.subscribe(
      (run_id) => {
        this.displayFeedbackSurvey = false;
        this.fetchRunExperiment(run_id);
    })
    // Subscriptions for feedback requests
    this.feedbackRequestSubscription = this.eventShareService.feedbackButtonClick$.subscribe(
      () => {
        this.displayFeedbackSurvey = false;
        console.log("Request arrived")
        this.feedback_markdown = 'Feedback requested, waiting for results...'
      }
    );
    this.feedbackReadySubscription = this.eventShareService.feedbackReady$.subscribe(
      (feedback_id) => {
        this.fetchRequestedFeedback(feedback_id);
        this.currentFeedbackID = feedback_id;
        if (sessionStorage.getItem("dataCollection") == "true"){
          this.displayFeedbackSurvey = true;
        }
        setTimeout(() => {}, 0);
    })
  }

  sendSurveyResults(surveyValue: any){
    const url = `${environment.apiUrl}/surveys/submit`;
    const data = {
      corresponding_id: this.currentFeedbackID,
      corresponding_id_type: "feedback_id",
      survey_results: surveyValue,
    }
    this.client.post(url, data, {withCredentials: true}).subscribe(
      (data) => {
        console.log("Survey results send")
      }
    );
  }

  hideSurveyForm(){
    this.displayFeedbackSurvey = false;
  }

  fetchSubmissionFeedback(submission_id: string) {
    console.log("fetchSubmissionFeedback", submission_id)
    const endpoint_url = `${environment.apiUrl}/submission/feedback/${submission_id}`;
    this.client.get<any>(endpoint_url, ).subscribe((data) => { 
      this.feedback = {
          test_results: data.test_results,
          task_id: data.task_unique_name,
          submission_id: data.submission_id,
          valid_solution: data.valid_solution,
      };
      this.feedback_markdown = this.renderTestResults(this.feedback["test_results"]!, this.feedback["task_id"]!);
      if(this.feedback["valid_solution"]) {
        this.openValidSolutionDialog();
      }
      //this.evaluateFeedback(this.feedback["valid_solution"]!);
      //this.feedback_string = JSON.stringify(this.feedback);
    });
  }

  renderTestResults(feedback_array: Array<any>, task_name: string) {
    var feedback_markdown = `# Feedback for task ${task_name}\n`;
    for (var test_obj of feedback_array) {
      feedback_markdown += "## " + test_obj["test_name"] + "\n";
      feedback_markdown += test_obj["message"];
      feedback_markdown += '\n';
    }
    return(feedback_markdown);
  }

  fetchRunExperiment(runId: string) {
      console.log("fetchRunExperiment", runId)
      const endpoint_url = `${environment.apiUrl}/submission/feedback/${runId}`;
      this.client.get<any>(endpoint_url, ).subscribe((data) => { 
        this.feedback = {
          output: data.run_output,
          task_id: data.task_unique_name,
      };
      this.feedback_markdown = data.run_output;
    });
  }

  fetchRequestedFeedback(feedbackID: string) {
    console.log("fetchRequestedFeedback", feedbackID)
      const endpoint_url = `${environment.apiUrl}/submission/feedback/${feedbackID}`;
      this.client.get<any>(endpoint_url, ).subscribe((data) => { 
        this.feedback = {
          feedback: data.feedback,
          task_id: data.task_unique_name,
      };
      this.feedback_markdown = data.feedback;
    });
  }

  openValidSolutionDialog()
  {
    this.taskSolvedDialog.nativeElement.showModal();
  }

  actOnValidSolution(action: string) {
    if (action == "stay") {
      this.taskSolvedDialog.nativeElement.close();
    }
    else if (action == "next task") {
      this.eventShareService.emitNewTaskEvent('personal');
      this.taskSolvedDialog.nativeElement.close();
    }
  }

  ngOnDestroy() {
    this.submitSubscription.unsubscribe();
    this.testReadySubscription.unsubscribe();
    this.newTaskSubscription.unsubscribe();
    this.codeRunSubscription.unsubscribe();
    this.codeRunReadySubscription.unsubscribe();
    this.feedbackRequestSubscription.unsubscribe();
    this.feedbackReadySubscription.unsubscribe();
  }
}
