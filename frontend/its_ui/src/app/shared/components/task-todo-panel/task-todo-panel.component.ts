import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MarkdownPanelComponent } from '../markdown-panel/markdown-panel.component';

/**
 * Small wrapper that renders a single task's "## To Do" section in a
 * scrollable, sticky-height container. Used in the right-hand editor pane
 * so the learner always sees the current objective above the Monaco
 * editor. Falls back to a generic instruction if the source markdown
 * contains no "To Do" heading.
 */
@Component({
  selector: 'app-task-todo-panel',
  templateUrl: './task-todo-panel.component.html',
  styleUrls: ['./task-todo-panel.component.css'],
  standalone: true,
  imports: [CommonModule, MatIconModule, MarkdownPanelComponent]
})
export class TaskTodoPanelComponent {
  /** Markdown string for the "## To Do" section, or a fallback. */
  @Input() todoMarkdown: string = '';
  /** True when no real To Do section was found and we're showing a default. */
  @Input() isFallback: boolean = false;
}
