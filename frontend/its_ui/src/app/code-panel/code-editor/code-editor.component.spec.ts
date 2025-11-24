import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeEditorNewComponent } from './code-editor-new.component';

describe('CodeEditorNewComponent', () => {
  let component: CodeEditorNewComponent;
  let fixture: ComponentFixture<CodeEditorNewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CodeEditorNewComponent]
    });
    fixture = TestBed.createComponent(CodeEditorNewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
