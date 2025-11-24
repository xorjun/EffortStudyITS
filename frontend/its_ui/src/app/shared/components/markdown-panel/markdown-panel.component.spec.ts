import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MarkdownPanelComponent } from './markdown-panel.component';

describe('MarkdownPanelComponent', () => {
  let component: MarkdownPanelComponent;
  let fixture: ComponentFixture<MarkdownPanelComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MarkdownPanelComponent]
    });
    fixture = TestBed.createComponent(MarkdownPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
