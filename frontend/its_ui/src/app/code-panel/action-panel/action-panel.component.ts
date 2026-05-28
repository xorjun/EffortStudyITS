import { Component, Output, EventEmitter, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { EventShareService } from 'src/app/shared/services/event-share.service';
import { CourseSettingsService } from 'src/app/shared/services/course-settings-service.service';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { RunParametersDialogComponent, RunParametersDialogResult } from './run-parameters-dialog/run-parameters-dialog.component';

@Component({
    selector: 'app-action-panel',
    templateUrl: './action-panel.component.html',
    styleUrls: ['./action-panel.component.css'],
    standalone: true,
    imports: [CommonModule, MatIconModule, MatTooltipModule, MatButtonModule, MatDialogModule]
})
export class ActionPanelComponent {

  @Output() runEvent: EventEmitter<{ parameters: any, showConsoleOutput: boolean }> = new EventEmitter<{ parameters: any, showConsoleOutput: boolean }>();
  @Output() submitEvent : EventEmitter<string> = new EventEmitter<string>();
  @Output() feedbackEvent : EventEmitter<string> = new EventEmitter<string>();

  taskFetchedSubscription?: Subscription;

  submissionId: string = '';
  course?: any;
  inCooldown: boolean = false;
  previousParameters: { [key: string]: string } = {};
  previousShowConsoleOutput: boolean = false;
  aiAssistanceMode: string = 'disabled';
  private cooldownTimeoutId: ReturnType<typeof setTimeout> | null = null;

  @Input() showRunButton: boolean = true;
  @Input() showFeedbackButton!: boolean;


  constructor(
    private eventShareService: EventShareService,
    private courseSettingsService: CourseSettingsService,
    private dialog: MatDialog
  ){}

  ngOnInit(){
    this.courseSettingsService.getCourse().subscribe((course)  =>
    {
      this.course = course
      this.aiAssistanceMode = this.course.course_settings_list?.[0]?.ai_assistance_mode || 'disabled';
      this.taskFetchedSubscription = this.eventShareService.newTaskFetched$.subscribe(() => {
        this.resetHintAvailability();
      }
      );
    });
  }

  ngOnDestroy() {
    this.taskFetchedSubscription?.unsubscribe();
    this.clearCooldownTimer();
  }

  get showHintButton(): boolean {
    return this.showFeedbackButton && this.aiAssistanceMode === 'hints';
  }

  get feedbackButtonLabel(): string {
    return this.aiAssistanceMode === 'hints' ? 'AI Hint' : 'Hint';
  }

  get feedbackTooltip(): string {
    if (this.inCooldown) {
      return 'Hint on cooldown';
    }
    return this.aiAssistanceMode === 'hints' ? 'Request an AI hint' : 'Request a hint';
  }

  runButtonClicked() {
    const taskType = sessionStorage.getItem("taskType");
    const taskArguments = sessionStorage.getItem("taskArguments");
    
    if (taskType === "function" && taskArguments) {
      const argumentsList: string[] = JSON.parse(taskArguments);
      const dialogRef = this.dialog.open(RunParametersDialogComponent, {
        data: {
          arguments: argumentsList,
          previousParameters: this.previousParameters,
          previousShowConsoleOutput: this.previousShowConsoleOutput
        },
        width: '500px'
      });

      dialogRef.afterClosed().subscribe((result: RunParametersDialogResult | undefined) => {
        if (result) {
          this.previousParameters = result.parameters;
          this.previousShowConsoleOutput = result.showConsoleOutput;
          this.emitRunEvent(result.parameters, result.showConsoleOutput);
        }
      });
    } else {
      this.emitRunEvent({}, this.previousShowConsoleOutput);
    }
  }

  emitRunEvent(parameters: any, showConsoleOutput: boolean = true) {
    this.runEvent.emit({ parameters, showConsoleOutput });
    this.eventShareService.emitRunButtonClick();
  }

  submitButtonClicked() {
    this.emitSubmitEvent();
  }

  emitSubmitEvent() {
    this.submitEvent.emit();
    this.eventShareService.emitSubmitButtonClick();
  }

  private clearCooldownTimer(): void {
    if (this.cooldownTimeoutId !== null) {
      clearTimeout(this.cooldownTimeoutId);
      this.cooldownTimeoutId = null;
    }
  }

  private resetHintAvailability(): void {
    this.clearCooldownTimer();
    this.inCooldown = false;
  }

  private startHintCooldown(durationMs: number): void {
    this.clearCooldownTimer();
    if (durationMs <= 0) {
      this.inCooldown = false;
      return;
    }
    this.inCooldown = true;
    this.cooldownTimeoutId = setTimeout(() => {
      this.inCooldown = false;
      this.cooldownTimeoutId = null;
    }, durationMs);
  }

  feedbackButtonClicked() {
    if (!this.inCooldown) {
      this.feedbackEvent.emit();
      this.eventShareService.emitFeedbackButtonClick();
      this.startHintCooldown(this.course.course_settings_list[0].feedback_cooldown*1000);
    }
    else {
      window.alert("New Feedback will not be available for a short time. Please Try to implement the suggestions of the last feedback first or try a new approach.")
    }
  }
}
