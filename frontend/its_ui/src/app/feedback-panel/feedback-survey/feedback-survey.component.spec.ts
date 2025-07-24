import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeedbackSurveyComponent } from './feedback-survey.component';

describe('FeedbackSurveyComponent', () => {
  let component: FeedbackSurveyComponent;
  let fixture: ComponentFixture<FeedbackSurveyComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [FeedbackSurveyComponent]
    });
    fixture = TestBed.createComponent(FeedbackSurveyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
