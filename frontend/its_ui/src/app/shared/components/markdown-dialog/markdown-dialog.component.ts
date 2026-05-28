import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MarkdownPanelComponent } from '../markdown-panel/markdown-panel.component';

export interface MarkdownDialogData {
  title: string;
  content: string;
}

@Component({
  selector: 'app-markdown-dialog',
  templateUrl: './markdown-dialog.component.html',
  styleUrls: ['./markdown-dialog.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MarkdownPanelComponent
  ]
})
export class MarkdownDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<MarkdownDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: MarkdownDialogData
  ) {}
}
