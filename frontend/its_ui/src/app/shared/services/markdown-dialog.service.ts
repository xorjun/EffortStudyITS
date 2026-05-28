import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { MarkdownDialogComponent, MarkdownDialogData } from '../components/markdown-dialog/markdown-dialog.component';

@Injectable({
  providedIn: 'root'
})
export class MarkdownDialogService {

  constructor(
    private dialog: MatDialog,
    private httpClient: HttpClient
  ) {}

  open(title: string, content: string): void {
    this.dialog.open(MarkdownDialogComponent, {
      data: { title, content } as MarkdownDialogData,
      maxWidth: '600px',
      width: '100%'
    });
  }

  openFromApi(title: string, endpoint: string): void {
    this.httpClient.get<any>(`${environment.apiUrl}${endpoint}`).subscribe({
      next: (data) => {
        const content = data[Object.keys(data)[0]];
        this.open(title, content);
      },
      error: (error) => {
        console.error('Error loading markdown content:', error);
        this.open(title, 'Error loading content.');
      }
    });
  }

  openAbout(): void {
    this.openFromApi('About', '/info/about');
  }

  openImprint(): void {
    this.openFromApi('Impressum', '/info/imprint');
  }

  openPrivacyPolicy(): void {
    this.openFromApi('Privacy Policy', '/info/privacy_policy');
  }

  openDataTerms(): void {
    this.openFromApi('Data Collection', '/info/data_collection');
  }
}
