import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CourseSettingsComponent } from './course-settings.component';

describe('CourseSettingsComponent', () => {
  let component: CourseSettingsComponent;
  let fixture: ComponentFixture<CourseSettingsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CourseSettingsComponent]
    });
    fixture = TestBed.createComponent(CourseSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
