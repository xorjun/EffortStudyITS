import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MonacoCodeEditorComponent } from './monaco-code-editor.component';

describe('MonacoCodeEditorComponent', () => {
  let component: MonacoCodeEditorComponent;
  let fixture: ComponentFixture<MonacoCodeEditorComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MonacoCodeEditorComponent]
    });
    fixture = TestBed.createComponent(MonacoCodeEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
