import { TestBed } from '@angular/core/testing';

import { MonacoEditoServiceService } from './monaco-edito-service.service';

describe('MonacoEditoServiceService', () => {
  let service: MonacoEditoServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MonacoEditoServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
