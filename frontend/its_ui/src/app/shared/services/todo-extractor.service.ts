import { Injectable } from '@angular/core';

/**
 * Helpers for slicing a "## To Do" (or similarly named) section out of a task
 * description markdown string.
 *
 * Task markdown is the same `task.md` shown in the left task panel. Each task
 * contains a section that lists the steps the learner should complete, headed
 * by `## To Do` (or `## To do`, `## Exercise`, `## TODO`, etc.). The right-hand
 * editor pane shows a sticky copy of just that section so the learner always
 * sees the current objective above the Monaco editor.
 */
@Injectable({
  providedIn: 'root'
})
export class TodoExtractorService {
  /**
   * Section headings that we treat as the "to do" section, in priority order.
   * The first heading found in the markdown wins; trailing whitespace is
   * tolerated.
   */
  private readonly todoHeadings: RegExp[] = [
    /^##\s+to\s*do\s*$/im,
    /^##\s+todo\s*$/im,
    /^##\s+exercise\s*$/im,
    /^##\s+task\s*$/im,
  ];

  /**
   * Returns the to-do / exercise section from a task markdown string, or
   * `null` if no matching heading is present. The returned string includes
   * the heading line itself and everything up to (but not including) the
   * next `## ` heading.
   */
  extractTodoSection(markdown: string | null | undefined): string | null {
    if (!markdown) {
      return null;
    }
    for (const heading of this.todoHeadings) {
      const match = heading.exec(markdown);
      if (!match) {
        continue;
      }
      const startIndex = match.index;
      const afterHeading = startIndex + match[0].length;
      const rest = markdown.slice(afterHeading);
      // Stop at the next level-2 heading. Level-1 (`# `) headings only
      // appear at the very top of the document (the task title) so they
      // don't need a special case.
      const nextHeading = /(^|\n)##\s/.exec(rest);
      const endIndex = nextHeading ? nextHeading.index + (nextHeading[1]?.length ?? 0) : rest.length;
      const section = rest.slice(0, endIndex).trim();
      if (section.length === 0) {
        return null;
      }
      // Re-prepend the heading so the markdown panel still renders the
      // "To Do" title above the steps.
      return `## To Do\n\n${section}`;
    }
    return null;
  }
}
