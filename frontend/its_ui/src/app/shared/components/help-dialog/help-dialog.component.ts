import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

interface HelpItem {
  /** Optional Material icon name for the item (left-aligned in the card). */
  icon?: string;
  /** Element name as it appears in the UI. */
  name: string;
  /** Where the element is located. */
  location: string;
  /** One-line description of what it does. */
  description: string;
  /**
   * Set to a string to hide this item unless the participant's condition
   * matches (e.g. 'A' for AI-Hint related items that should not surface
   * for Condition B participants).
   */
  visibleTo?: 'A' | 'B';
}

interface HelpSection {
  title: string;
  icon: string;
  items: HelpItem[];
}

export interface HelpDialogData {
  participantCondition?: 'A' | 'B' | null;
}

@Component({
  selector: 'app-help-dialog',
  templateUrl: './help-dialog.component.html',
  styleUrls: ['./help-dialog.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatTabsModule,
    MatDividerModule,
    MatTooltipModule,
    MatFormFieldModule,
    MatInputModule
  ]
})
export class HelpDialogComponent {
  /**
   * Static, curated help content. Each section is a tab in the dialog; each
   * entry is a UI element with a one-line plain-language description.
   */
  readonly sections: HelpSection[] = [
    {
      title: 'Navigation',
      icon: 'toolbar',
      items: [
        {
          icon: 'home',
          name: 'SCRIPT Logo',
          location: 'Top-left of the toolbar',
          description: 'Click the SCRIPT logo to return to the course selection screen at any time.',
        },
        {
          icon: 'topic',
          name: 'Topic Selector',
          location: 'Top-right, e.g. "1/2 Python Basics"',
          description: 'Click to open a menu of course topics; pick one to switch to its first task.',
        },
        {
          icon: 'chevron_left',
          name: 'Previous Task',
          location: 'Left arrow beside the task name',
          description: 'Step back one task within the current topic.',
        },
        {
          icon: 'chevron_right',
          name: 'Next Task',
          location: 'Right arrow beside the task name',
          description: 'Step forward one task within the current topic.',
        },
        {
          icon: 'bubble_chart',
          name: 'Task Status Bubbles',
          location: 'Row of small circles under the task name',
          description: 'Each dot is one task: empty = not started, half-filled = attempted, filled = completed. Click any dot to jump to that task.',
        },
        {
          icon: 'help_outline',
          name: 'Help Button',
          location: 'Top-right, just left of the menu',
          description: 'You are here — re-open this guide any time.',
        },
        {
          icon: 'menu',
          name: 'More Menu',
          location: 'Top-right corner (hamburger icon)',
          description: 'Opens About, Impressum, Privacy Policy, your Profile, and Skill Overview.',
        },
      ],
    },
    {
      title: 'Workspace',
      icon: 'code',
      items: [
        {
          icon: 'description',
          name: 'Task Description',
          location: 'Left panel',
          description: 'Markdown-rendered instructions for the current task, including the numbered "To Do" steps you need to follow.',
        },
        {
          icon: 'code',
          name: 'Code Editor (Monaco)',
          location: 'Center panel',
          description: 'Where you write your Python solution. Edits are saved automatically as you type.',
        },
        {
          icon: 'play_arrow',
          name: 'Run Button',
          location: 'Below the editor',
          description: 'Executes your code so you can see the output, but does not count as a submission.',
        },
        {
          icon: 'check_circle',
          name: 'Submit Button',
          location: 'Below the editor, beside Run',
          description: 'Runs the hidden unit tests. If all pass, the task is marked complete and the next task unlocks.',
        },
        {
          icon: 'auto_awesome',
          name: 'AI Hint Button',
          location: 'Below the editor (Condition A only)',
          description: 'Sends your current code to the tutor model for a step-by-step hint. Subject to per-session and per-day rate limits.',
          visibleTo: 'A',
        },
        {
          icon: 'feedback',
          name: 'Feedback Panel',
          location: 'Right side, or under the editor on small screens',
          description: 'Shows tutor hints (Condition A only), run output, submission results, and error traces.',
        },
        {
          icon: 'restart_alt',
          name: 'Reset / Revert',
          location: 'Inside the editor toolbar (right side)',
          description: 'Restores the task to the original starter code. Use it if you want to start over.',
        },
      ],
    },
    {
      title: 'Skill Overview',
      icon: 'analytics',
      items: [
        {
          icon: 'radar',
          name: 'Competency Radar',
          location: 'Main area of the Skill Overview screen',
          description: 'Each axis is one Python competency (e.g. "lists", "loops"). The filled area shows your current mastery estimate.',
        },
        {
          icon: 'list_alt',
          name: 'Competency List',
          location: 'Below the radar',
          description: 'Numerical breakdown of estimated mastery per skill, sorted from weakest to strongest.',
        },
        {
          icon: 'flag',
          name: 'Open Tasks',
          location: 'Bottom of the screen',
          description: 'Tasks that target skills where you have low mastery — recommended next tasks.',
        },
      ],
    },
    {
      title: 'Course Selection',
      icon: 'library_books',
      items: [
        {
          icon: 'book',
          name: 'Course Cards',
          location: 'Main area',
          description: 'One card per available course. Click a card to open the course overview and start its first task.',
        },
        {
          icon: 'upload',
          name: 'Upload Course (Admin)',
          location: 'Top-right, visible to admins only',
          description: 'Upload a course zip to add a new course. The zip must contain exactly one top-level course folder.',
        },
        {
          icon: 'logout',
          name: 'Profile / Logout',
          location: 'Top-right, behind the menu',
          description: 'View or edit your account details, and log out at the end of a session.',
        },
      ],
    },
    {
      title: 'Study Tips',
      icon: 'tips_and_updates',
      items: [
        {
          icon: 'save',
          name: 'Auto-save',
          location: 'Everywhere',
          description: 'Edits in the code editor are saved automatically — there is no explicit Save button. Just close the tab and come back later.',
        },
        {
          icon: 'search',
          name: 'Read the error',
          location: 'Feedback panel',
          description: 'When a submission fails, the right panel shows the test that failed and the error message. Read it carefully — for Condition A, ask the AI Hint a specific question based on it.',
        },
        {
          icon: 'forum',
          name: 'Ask focused questions',
          location: 'AI Hint (Condition A)',
          description: 'Type the specific thing you are stuck on ("why does my loop skip the last item?") rather than a vague "help".',
          visibleTo: 'A',
        },
        {
          icon: 'coffee',
          name: 'Take breaks',
          location: 'Between tasks',
          description: 'Each session targets one new concept. If you have been working for 30+ minutes, take a short break before continuing.',
        },
        {
          icon: 'privacy_tip',
          name: 'Your data is private',
          location: 'Account & Privacy',
          description: 'Clipboard events, code snapshots, and AI hint usage are only collected if you have given consent (Data Collection = on). You can withdraw consent any time from your profile.',
        },
      ],
    },
    {
      title: 'Session Controls',
      icon: 'timer',
      items: [
        {
          icon: 'hourglass_top',
          name: '5-minute skip lock',
          location: 'Top-right, next to the task name',
          description: 'The Next Task button (and forward-skipping via the task bubbles) is hidden for the first 5 minutes of every session so you have time to work through the current task before moving on.',
        },
        {
          icon: 'visibility',
          name: 'See the reference solution',
          location: 'Feedback panel, after a failed submission',
          description: 'When your submission does not pass the hidden tests, the feedback panel shows your code side-by-side with the reference solution so you can compare them. This only appears after at least one failed submission.',
        },
        {
          icon: 'lock_clock',
          name: 'Why a 5-minute lock?',
          location: 'Study protocol',
          description: 'The first few minutes of a task are often when you make your biggest learning gains. The lock keeps you from skipping too soon out of frustration, and the reference solution is the safety valve once you have genuinely tried.',
        },
      ],
    },
  ];

  // All sections, including a Condition B-specific section that only shows
  // for participants in that condition.
  private readonly conditionBSection: HelpSection = {
    title: 'Working Without AI Help',
    icon: 'self_improvement',
    items: [
      {
        icon: 'menu_book',
        name: 'Read the task description twice',
        location: 'Left panel',
        description: 'For Condition B, the task description is your primary guide. Re-read the "To Do" steps before each attempt and tick them off in order.',
        visibleTo: 'B',
      },
      {
        icon: 'lightbulb',
        name: 'Use the editor autocomplete',
        location: 'Center panel',
        description: 'The Monaco editor offers Python keyword and built-in completions. Press Ctrl+Space to trigger suggestions — useful when you forget a method name.',
        visibleTo: 'B',
      },
      {
        icon: 'play_arrow',
        name: 'Run, then read the error',
        location: 'Below the editor',
        description: 'Use the Run button to test your code without submitting. Read the output and error trace carefully before re-running.',
        visibleTo: 'B',
      },
      {
        icon: 'science',
        name: 'Experiment in small steps',
        location: 'Editor',
        description: 'Try small modifications, run after each one, and watch how the output changes. The Submit button is for final answers, not exploration.',
        visibleTo: 'B',
      },
    ],
  };

  /** Live-filtered view of `sections` based on `searchQuery` and condition. */
  filteredSections: HelpSection[] = this.computeFilteredSections();

  /** Current search text. Empty string means "show everything". */
  searchQuery = '';

  /** Currently selected tab index. Tracked so clearing the search keeps the user on the same section. */
  selectedTabIndex = 0;

  constructor(
    public dialogRef: MatDialogRef<HelpDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: HelpDialogData,
  ) {}

  /**
   * Build the section list for the current participant. Items marked with
   * `visibleTo: 'A'` or `visibleTo: 'B'` are hidden unless the participant's
   * condition matches. The Condition-B-specific section is only included for
   * Condition B participants.
   */
  private computeFilteredSections(): HelpSection[] {
    const condition = this.data?.participantCondition ?? null;
    const baseSections = this.sections.map((section) => ({
      ...section,
      items: section.items.filter(
        (item) => !item.visibleTo || item.visibleTo === condition,
      ),
    }));
    if (condition === 'B') {
      return [...baseSections, this.conditionBSection];
    }
    return baseSections;
  }

  onSearchChange(): void {
    const q = this.searchQuery.trim().toLowerCase();
    if (!q) {
      this.filteredSections = this.sections;
      return;
    }
    this.filteredSections = this.sections
      .map((section) => ({
        ...section,
        items: section.items.filter(
          (item) =>
            item.name.toLowerCase().includes(q) ||
            item.description.toLowerCase().includes(q) ||
            item.location.toLowerCase().includes(q),
        ),
      }))
      .filter((section) => section.items.length > 0);
    // If the current tab is now empty, jump to the first tab that has matches.
    if (
      this.filteredSections.length > 0 &&
      !this.filteredSections[this.selectedTabIndex]
    ) {
      this.selectedTabIndex = 0;
    }
  }

  clearSearch(): void {
    this.searchQuery = '';
    this.onSearchChange();
  }

  onTabChange(index: number): void {
    this.selectedTabIndex = index;
  }

  close(): void {
    this.dialogRef.close();
  }
}
