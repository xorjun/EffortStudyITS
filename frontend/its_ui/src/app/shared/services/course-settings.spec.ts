import { TestBed } from '@angular/core/testing';

import { CourseSettingsService } from './course-settings-service.service';

describe('CourseSettingsServiceService', () => {
  let service: CourseSettingsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CourseSettingsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
