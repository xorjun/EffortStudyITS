import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup, FormControl} from '@angular/forms';

@Component({
  selector: 'app-feedback-survey',
  templateUrl: './feedback-survey.component.html',
  styleUrls: ['./feedback-survey.component.css']
})
export class FeedbackSurveyComponent {

  @Output() surveyFilled : EventEmitter<any> = new EventEmitter<any>();
  @Output() hideForm : EventEmitter<string> = new EventEmitter<string>();
  surveyForm: FormGroup;

  usefulRatingText: string = "";
  relatedRatingText: string = "";

  constructor(){
    this.surveyForm = new FormGroup({
      usefullRating: new FormControl(''),
      relatedRating: new FormControl(''),
    });
    this.surveyForm.valueChanges.subscribe(data => this.onFormChange());
  }


  onFormChange() {
    this.usefulRatingText = this.getRatingText(this.surveyForm.get("usefullRating")!.value);
    this.relatedRatingText = this.getRatingText(this.surveyForm.get("relatedRating")!.value);
    this.surveyFilled.emit(this.surveyForm.value);
  }

  getRatingText(formValue: any){
    var ratingText: string = "";
    switch (formValue){
      case 1:
        ratingText = "(Strongly disagree)";
        break;
      case 2:
        ratingText = "(Disagree)";
        break;
      case 3:
        ratingText = "(Neutral)";
        break;
      case 4:
        ratingText = "(Agree)";
        break;
      case 5:
        ratingText = "(Strongly Agree)";
    }
    return(ratingText);
  }

  hideButtonClicked() {
    this.hideForm.emit("hide")
  }

  ngOnInit() {
  }

}
