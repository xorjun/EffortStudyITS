import { HttpClient } from '@angular/common/http';
import { Component, ViewChild, ElementRef } from '@angular/core';
import { environment } from 'src/environments/environment';
import { MarkdownPanelComponent } from '../markdown-panel/markdown-panel.component';

@Component({
    selector: 'app-privacy-policy-popup',
    templateUrl: './privacy-policy-popup.component.html',
    styleUrls: ['./privacy-policy-popup.component.css'],
    imports: [MarkdownPanelComponent]
})
export class PrivacyPolicyPopupComponent {

  @ViewChild("privacyPolicyPopup", {static: true}) privacyPolicyPopup!: ElementRef<HTMLDialogElement>

  privacyPolicyMarkdown: string = '';

  constructor(private httpClient: HttpClient){}


  showPopup() {
    this.httpClient.get<any>(`${environment.apiUrl}/info/privacy_policy`)
    .subscribe(data => {
      this.privacyPolicyMarkdown = data.privacy_policy_markdown;
    });
    this.privacyPolicyPopup.nativeElement.showModal();
    }
}
