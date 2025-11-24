import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImprintPopupComponent } from './imprint-popup.component';

describe('ImprintPopupComponent', () => {
  let component: ImprintPopupComponent;
  let fixture: ComponentFixture<ImprintPopupComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ImprintPopupComponent]
    });
    fixture = TestBed.createComponent(ImprintPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
