import { Component, Output, EventEmitter, ElementRef, ViewChild, Input, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup } from '@angular/forms';
import { Subscription } from 'rxjs';
import { EventShareService } from 'src/app/shared/services/event-share.service';
import { CourseSettingsService } from 'src/app/shared/services/course-settings-service.service';

@Component({
  selector: 'app-action-panel',
  templateUrl: './action-panel.component.html',
  styleUrls: ['./action-panel.component.css']
})
export class ActionPanelComponent {

  @Output() runEvent: EventEmitter<string> = new EventEmitter<any>();
  @Output() submitEvent : EventEmitter<string> = new EventEmitter<string>();
  @Output() feedbackEvent : EventEmitter<string> = new EventEmitter<string>();

  taskFetchedSubscription?: Subscription;


  @ViewChild("runDialog", {static: true}) runDialog!: ElementRef<HTMLDialogElement>

  submissionId: string = '';
  runParametersForm!: FormGroup;
  course?: any;
  inCooldown: boolean = false;

  @Input() showRunButton: boolean = true;
  @Input() showFeedbackButton!: boolean;


  constructor(private eventShareService: EventShareService,
              private fb: FormBuilder, private courseSettingsService: CourseSettingsService){
              }

  ngOnInit(){
    this.courseSettingsService.getCourse().subscribe((course)  =>
    {
      this.course = course
      this.taskFetchedSubscription = this.eventShareService.newTaskFetched$.subscribe((data) => {
        this.inCooldown = true;
        setTimeout(() => {
          this.inCooldown = false;
        }, this.course.course_settings.feedback_init_time*1000);
      }
      );
    });
  }

  parameterFormArrayControls() {
    const controls: FormGroup[] = [];

    const argArray: string[] = JSON.parse(sessionStorage.getItem("taskArguments")!);
    if (!argArray) {
      console.error("taskArguments is not present in sessionStorage.");
    }
    for (let i = 0; i < argArray.length; i++) {
      controls.push(this.fb.group({
        // You can add any validators or default values here
        argname: argArray[i],
        textField: [''],
      }));
    }
    return controls;
  }

  get runFormArrayControls() {
    return (this.runParametersForm.get('fields') as FormArray).controls;
  }

  runButtonClicked() {
    if(sessionStorage.getItem("taskType") == "function") {
      this.runParametersForm = this.fb.group({
        fields: this.fb.array(this.parameterFormArrayControls())
      });
      this.runDialog.nativeElement.showModal();
    }
    else {
      this.emitRunEvent({});
    }
  }

  sendWithParameters() {
    var parameters: any = {};
    const count = JSON.parse(sessionStorage.getItem("taskArguments")!).length;
    for (let i = 0; i < count; i++) {
      const control = this.runFormArrayControls.at(i)!;
      const key = control.get('argname')!.value;
      const value = control.get('textField')!.value;
      parameters[key] = value;
    }
    this.runDialog.nativeElement.close();
    this.emitRunEvent(parameters);
  }

  emitRunEvent(parameters: any) {
    this.runEvent.emit(parameters);
    this.eventShareService.emitRunButtonClick();
  }

  //Submit Button
  submitButtonClicked() {
    this.submitEvent.emit();
    this.eventShareService.emitSubmitButtonClick();
  }

  // Feedback Button
  feedbackButtonClicked() {
    if (!this.inCooldown) {
      this.feedbackEvent.emit();
      this.eventShareService.emitFeedbackButtonClick();
      this.inCooldown = true;
      setTimeout(() => {
        this.inCooldown = false;
      }, this.course.course_settings.feedback_cooldown*1000);
    }
    else {
      window.alert("New Feedback will not be available for a short time. Please Try to implement the suggestions of the last feedback first or try a new approach.")
    }
  }
}