import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SettingsElementComponent } from './settings-element.component';

describe('SettingsElementComponent', () => {
  let component: SettingsElementComponent;
  let fixture: ComponentFixture<SettingsElementComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SettingsElementComponent]
    });
    fixture = TestBed.createComponent(SettingsElementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
