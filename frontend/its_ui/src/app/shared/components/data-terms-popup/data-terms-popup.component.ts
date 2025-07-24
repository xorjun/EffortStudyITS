import { HttpClient } from '@angular/common/http';
import { Component, ViewChild, ElementRef, Input,  } from '@angular/core';
import { environment } from 'src/environments/environment';
import { MarkdownComponent } from 'ngx-markdown';

@Component({
  selector: 'app-data-terms-popup',
  templateUrl: './data-terms-popup.component.html',
  styleUrls: ['./data-terms-popup.component.css']
})
export class DataTermsPopupComponent {

  @ViewChild("dataTermsPopup", {static: true}) dataTermsPopup!: ElementRef<HTMLDialogElement>

  dataCollectionMarkdown: string = '';

  constructor(private httpClient: HttpClient){}


  showPopup() {
    this.httpClient.get<any>(`${environment.apiUrl}/info/data_collection`)
    .subscribe(data => {
      this.dataCollectionMarkdown = data.data_collection_markdown;
    });
    this.dataTermsPopup.nativeElement.showModal();
    }
}
