import { HttpClient } from '@angular/common/http';
import { Component, ViewChild, ElementRef } from '@angular/core';
import { environment } from 'src/environments/environment';
import { MarkdownPanelComponent } from '../markdown-panel/markdown-panel.component';

@Component({
    selector: 'app-imprint-popup',
    templateUrl: './imprint-popup.component.html',
    styleUrls: ['./imprint-popup.component.css'],
    imports: [MarkdownPanelComponent]
})
export class ImprintPopupComponent {

  @ViewChild("imprintPopup", {static: true}) imprintPopup!: ElementRef<HTMLDialogElement>

  imprintMarkdown: string = '';

  constructor(private httpClient: HttpClient){console.log('constructor')}


  showPopup() {
    this.httpClient.get<any>(`${environment.apiUrl}/info/imprint`)
    .subscribe(data => {
      this.imprintMarkdown = data.imprint_markdown;
    });
    this.imprintPopup.nativeElement.showModal();
    }
}
