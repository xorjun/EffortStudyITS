import { Component, ElementRef, ViewChild, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { EventShareService } from '../shared/services/event-share.service';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { MarkdownPanelComponent } from '../shared/components/markdown-panel/markdown-panel.component';
import { FeedbackSurveyComponent } from './feedback-survey/feedback-survey.component';
import { StudyTelemetryService } from '../shared/services/study-telemetry.service';
import { ExternalFeedbackPayload } from '../shared/services/event-share.service';

@Component({
    selector: 'app-feedback-panel',
    templateUrl: './feedback-panel.component.html',
    styleUrls: ['./feedback-panel.component.css'],
    imports: [CommonModule, MarkdownPanelComponent, FeedbackSurveyComponent, MatTooltipModule, MatIconModule]
})
export class FeedbackPanelComponent implements OnDestroy {
  show: boolean = true

  @ViewChild("taskSolvedDialog", {static: true}) taskSolvedDialog!: ElementRef<HTMLDialogElement>;
  @ViewChild("graphComparisonDialog", {static: true}) graphComparisonDialog!: ElementRef<HTMLDialogElement>;

  private submitSubscription: Subscription;
  private testReadySubscription: Subscription;
  private newTaskSubscription: Subscription;
  private codeRunSubscription: Subscription;
  private codeRunReadySubscription: Subscription;
  private feedbackRequestSubscription: Subscription;
  private feedbackReadySubscription: Subscription;
  private externalFeedbackSubscription: Subscription;

  code_language: string = 'python';
  feedback_markdown: string = '';
  graph_solution: string = '';
  graph_result: string = '';
  feedback:  { test_results?: Array<any>; task_id?: string; submission_id?: string; 
    valid_solution?: boolean, output?: boolean, feedback?: string} = {};
  submissionId: string = '';
  displayFeedbackSurvey = false;
  currentFeedbackID: string = "";
  

  constructor(
    private eventShareService: EventShareService,
    private client: HttpClient,
    private studyTelemetryService: StudyTelemetryService,){
    //Subscriptions for code submit
    this.submitSubscription = this.eventShareService.submitButtonClick$.subscribe((data) => {
      this.feedback_markdown = 'Code submitted, waiting for feedback...';
      this.graph_solution = '';
      this.graph_result = '';
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
        this.feedback_markdown = 'AI hint requested, waiting for results...'
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
    });
    this.externalFeedbackSubscription = this.eventShareService.externalFeedback$.subscribe(
      (payload: ExternalFeedbackPayload) => {
        this.displayFeedbackSurvey = false;
        this.feedback_markdown = payload.markdown;
        this.currentFeedbackID = payload.feedbackId || payload.source;
        this.studyTelemetryService.logContextEvent('feedback-result', {
          feedbackId: this.currentFeedbackID,
          source: payload.source,
          feedbackLength: payload.markdown.length,
        });
      }
    );
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
      const failedTests = Array.isArray(data.test_results)
        ? data.test_results.filter((result: { status?: boolean }) => !result.status).length
        : 0;
      this.feedback = {
          test_results: data.test_results,
          task_id: data.task_unique_name,
          submission_id: data.submission_id,
          valid_solution: data.valid_solution,
      };
      this.studyTelemetryService.logContextEvent('submission-result', {
        submissionId: data.submission_id,
        validSolution: data.valid_solution,
        testCount: Array.isArray(data.test_results) ? data.test_results.length : 0,
        failedTests,
      });
      this.feedback_markdown = this.renderTestResults(this.feedback["test_results"]!, this.feedback["task_id"]!);
      // Every submission also produces a plain-English summary of what the
      // learner's code achieves, shown above the test results. The summary
      // is static-analysis based (always works) and optionally enriched
      // with an LLM one-liner by the backend.
      this.fetchCodeSummary(submission_id);
      if(sessionStorage.getItem("taskType")! == "plot_function") {
        this.graph_result = ''
        for (var test_obj of this.feedback["test_results"]!) {
          this.graph_result += test_obj["message"];
        }
        this.graph_solution = data.reference_output
        this.openGraphComparisonDialog();
      }
      else if(this.feedback["valid_solution"]) {
        this.studyTelemetryService.logContextEvent('task-solved', {
          submissionId: data.submission_id,
          via: 'submission',
        });
        this.openValidSolutionDialog();
      }
      else {
        // Incorrect, non-plot submission: also fetch the reference solution
        // so the learner can compare their code with the model solution. The
        // backend only returns it after at least one failed submission for
        // this task, so this is a safe "give up" reward. Plot tasks are
        // graded by the graph comparison dialog above and do not need a
        // code comparison.
        this.fetchReferenceComparison(data);
      }
      //this.evaluateFeedback(this.feedback["valid_solution"]!);
      //this.feedback_string = JSON.stringify(this.feedback);
    });
  }

  /**
   * When a submission is not correct, fetch the reference solution and append
   * a "Your code vs. Reference solution" section to the feedback panel. The
   * backend enforces that this is only available after a failed submission,
   * so the comparison is only ever shown when the learner has already tried.
   */
  private fetchReferenceComparison(submissionData: any): void {
    const taskId = submissionData?.task_unique_name;
    if (!taskId) {
      return;
    }
    const userCode: string = submissionData?.code ?? '';
    this.client.get<any>(`${environment.apiUrl}/task/reference_solution/${taskId}`, { withCredentials: true })
      .subscribe({
        next: (ref) => {
          this.feedback_markdown += this.renderCodeComparison(userCode, ref?.example_solution ?? '');
        },
        // 403 / 404 just means the reference is not (yet) available — keep
        // the standard test feedback visible in that case.
        error: () => { /* no-op */ }
      });
  }

  /**
   * Render a side-by-side comparison of the learner's submitted code and the
   * task's example solution. Returned as a markdown block so it integrates
   * with the existing markdown panel rendering.
   */
  private renderCodeComparison(userCode: string, referenceCode: string): string {
    const escape = (s: string) => (s ?? '').replace(/```/g, '`\u200b``');
    let md = `\n\n## Code Comparison\n\n`;
    md += `Your submission did not pass the hidden tests. Below is your code `;
    md += `next to the reference solution so you can spot the difference.\n\n`;
    md += `### Your code\n\n`;
    md += '```python\n' + escape(userCode) + '\n```\n\n';
    md += `### Reference solution\n\n`;
    md += '```python\n' + escape(referenceCode) + '\n```\n';
    return md;
  }

  /**
   * Fetch a plain-English summary of what the user's submitted code
   * achieves and prepend it to the feedback panel. The backend always
   * returns a deterministic AST-based summary; an LLM-enriched variant is
   * appended when available. This is shown on every submission (passing
   * or failing) so the learner always gets a "what does my code do"
   * signal regardless of the test outcome.
   */
  private fetchCodeSummary(submissionId: string): void {
    this.client.get<any>(`${environment.apiUrl}/submission/summary/${submissionId}`, { withCredentials: true })
      .subscribe({
        next: (data) => {
          const block = this.renderCodeSummary(
            data?.static_summary,
            data?.llm_summary,
          );
          if (block) {
            this.feedback_markdown = block + this.feedback_markdown;
          }
        },
        // 404 / 500 just means the summary is not (yet) available — keep
        // the standard test feedback visible in that case.
        error: () => { /* no-op */ }
      });
  }

  /**
   * Render the "What your code achieves" block as markdown so it integrates
   * with the rest of the feedback panel. The static summary is always
   * shown when present; the LLM one-liner, if any, is shown as a quoted
   * sub-section beneath it.
   */
  private renderCodeSummary(staticSummary: string | null | undefined, llmSummary: string | null | undefined): string {
    if (!staticSummary && !llmSummary) {
      return '';
    }
    let md = `## What your code achieves\n\n`;
    if (staticSummary) {
      md += staticSummary.trim() + '\n';
    }
    if (llmSummary) {
      md += `\n> ${llmSummary.trim().replace(/\n+/g, ' ')}\n`;
    }
    md += '\n---\n\n';
    return md;
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
        const combinedOutput = `${data.run_output || ''}\n${data.console_output || ''}`.toLowerCase();
        const looksLikeError = ['traceback', 'error', 'exception'].some((needle) => combinedOutput.includes(needle));
        this.feedback = {
          output: data.run_output,
          task_id: data.task_unique_name,
      };
      this.studyTelemetryService.logContextEvent('run-result', {
        runId,
        outputLength: typeof data.run_output === 'string' ? data.run_output.length : 0,
        consoleOutputLength: typeof data.console_output === 'string' ? data.console_output.length : 0,
        looksLikeError,
      });
      let markdown = '## Result\n\n' + data.run_output;
      if (data.console_output && data.console_output.trim() !== '') {
        markdown += '\n\n## Console Output\n\n```\n' + data.console_output + '\n```';
      }
      this.feedback_markdown = markdown;
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
      this.studyTelemetryService.logContextEvent('feedback-result', {
        feedbackId: feedbackID,
        source: 'legacy',
        feedbackLength: typeof data.feedback === 'string' ? data.feedback.length : 0,
      });
      this.feedback_markdown = data.feedback;
    });
  }

  openValidSolutionDialog() {
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

  openGraphComparisonDialog() {
    this.graphComparisonDialog.nativeElement.showModal();
  }

  // TODO make solution go valid
  actOnGraphComparison(action: string) {
    if (action == "stay") {
      this.graphComparisonDialog.nativeElement.close();
    }
    else if (action == "next task") {
      this.feedback["valid_solution"] = true
      const endpoint_url = `${environment.apiUrl}/mark_solved/${sessionStorage.getItem("taskId")}`;
      this.client.post<any>(endpoint_url, {}, {withCredentials: true}).subscribe((data) => {
        this.studyTelemetryService.logContextEvent('task-solved', {
          via: 'plot-comparison',
        });
      })
      this.eventShareService.emitNewTaskEvent('personal');
      this.graphComparisonDialog.nativeElement.close();
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
    this.externalFeedbackSubscription.unsubscribe();
  }
}
