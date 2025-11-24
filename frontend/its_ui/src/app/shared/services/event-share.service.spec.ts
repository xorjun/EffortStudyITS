import { TestBed } from '@angular/core/testing';

import { EventShareService } from './event-share.service';

describe('EventShareService', () => {
  let service: EventShareService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EventShareService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
