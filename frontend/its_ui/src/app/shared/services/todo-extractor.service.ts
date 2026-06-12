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
    const range = this.findTodoRange(markdown);
    if (!range) {
      return null;
    }
    const section = markdown.slice(range.start, range.end).trim();
    if (section.length === 0) {
      return null;
    }
    // Re-prepend the heading so the markdown panel still renders the
    // "To Do" title above the steps.
    return `## To Do\n\n${section}`;
  }

  /**
   * Returns the same task markdown with the `## To Do` section removed.
   * The matching `---` separator (or surrounding blank lines) directly
   * before the section is also dropped so the result reads cleanly.
   * If no to-do section is found, the markdown is returned unchanged.
   */
  stripTodoSection(markdown: string | null | undefined): string {
    if (!markdown) {
      return '';
    }
    const range = this.findTodoRange(markdown);
    if (!range) {
      return markdown;
    }
    // Extend the cut a little to the left so a trailing `---` separator
    // directly above the section is consumed too. We do not eat more than
    // one preceding blank line to avoid eating content from the previous
    // section.
    let cutStart = range.start;
    const before = markdown.slice(0, cutStart);
    const sepMatch = /\n[ \t]*-{3,}[ \t]*\n[ \t]*$/.exec(before);
    if (sepMatch) {
      cutStart -= sepMatch[0].length;
    } else {
      // Drop at most one preceding blank line so we don't glue the
      // next section's heading directly onto the previous paragraph.
      cutStart = Math.max(0, cutStart - 1);
      while (cutStart > 0 && /\s/.test(markdown[cutStart - 1])) {
        cutStart -= 1;
      }
    }
    return (markdown.slice(0, cutStart) + markdown.slice(range.end)).replace(/\n{3,}/g, '\n\n').trimEnd() + '\n';
  }

  /**
   * Locate the to-do section's [start, end) range in `markdown` (start is
   * the index of the heading line; end is one past the last character
   * before the next `## ` heading or end-of-document). Returns `null` if
   * no matching heading is present.
   */
  private findTodoRange(markdown: string): { start: number; end: number } | null {
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
      const endOffset = nextHeading ? nextHeading.index + (nextHeading[1]?.length ?? 0) : rest.length;
      return { start: startIndex, end: afterHeading + endOffset };
    }
    return null;
  }
}
