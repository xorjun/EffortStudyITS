import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PrivacyPolicyPopupComponent } from './privacy-policy-popup.component';

describe('PrivacyPolicyPopupComponent', () => {
  let component: PrivacyPolicyPopupComponent;
  let fixture: ComponentFixture<PrivacyPolicyPopupComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PrivacyPolicyPopupComponent]
    });
    fixture = TestBed.createComponent(PrivacyPolicyPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
