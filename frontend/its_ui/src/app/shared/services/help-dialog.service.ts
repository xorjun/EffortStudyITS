import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { HelpDialogComponent, HelpDialogData } from '../components/help-dialog/help-dialog.component';
import { StudyContextService } from './study-context.service';

@Injectable({
  providedIn: 'root'
})
export class HelpDialogService {
  constructor(
    private dialog: MatDialog,
    private studyContext: StudyContextService,
  ) {}

  /**
   * Opens the platform help dialog. Idempotent: if a help dialog is already
   * open, this is a no-op so the user does not end up with stacked dialogs.
   * The dialog is shown with the participant's condition so that AI-hint
   * entries can be hidden for Condition B.
   */
  open(): void {
    if (this.dialog.openDialogs.some((d) => d.componentInstance instanceof HelpDialogComponent)) {
      return;
    }
    const condition = (this.studyContext.snapshot.condition as 'A' | 'B' | null) ?? null;
    this.dialog.open<HelpDialogComponent, HelpDialogData>(HelpDialogComponent, {
      data: { participantCondition: condition },
      maxWidth: '960px',
      width: '100%',
      panelClass: 'help-dialog-panel',
      autoFocus: 'first-tabbable',
    });
  }
}
