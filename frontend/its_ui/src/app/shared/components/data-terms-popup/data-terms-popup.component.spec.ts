import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataTermsPopupComponent } from './data-terms-popup.component';

describe('DataTermsPopupComponent', () => {
  let component: DataTermsPopupComponent;
  let fixture: ComponentFixture<DataTermsPopupComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DataTermsPopupComponent]
    });
    fixture = TestBed.createComponent(DataTermsPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
