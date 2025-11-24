import { HttpClient } from '@angular/common/http';
import { Component, ViewChild, ElementRef, Input,  } from '@angular/core';
import { environment } from 'src/environments/environment';
import { MarkdownComponent } from 'ngx-markdown';

@Component({
  selector: 'app-privacy-policy-popup',
  templateUrl: './privacy-policy-popup.component.html',
  styleUrls: ['./privacy-policy-popup.component.css']
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
