import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CourseSelectionPanelComponent } from './course-selection-panel.component';

describe('CourseSelectionPanelComponent', () => {
  let component: CourseSelectionPanelComponent;
  let fixture: ComponentFixture<CourseSelectionPanelComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CourseSelectionPanelComponent]
    });
    fixture = TestBed.createComponent(CourseSelectionPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
