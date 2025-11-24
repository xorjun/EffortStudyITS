import { AfterViewInit, Component, ElementRef, Input, OnChanges, ViewChild } from '@angular/core';
import * as Prism from 'prismjs';

// source: https://techincent.com/code-syntax-highlighter-angular-with-prism-js/
// Consult source if multiple languages are required.

@Component({
  selector: 'app-prism',
  templateUrl: './prism.component.html',
  styleUrls: ['./prism.component.css']
})
export class PrismComponent implements AfterViewInit, OnChanges {
  @ViewChild('codeEle') codeEle!: ElementRef;
  @Input() code?: string;
  @Input() language?: string;
  constructor() { }
  ngAfterViewInit() {
    Prism.highlightElement(this.codeEle.nativeElement);
  }


  ngOnChanges(changes: any): void {
    if (changes?.code) {
      console.log("changes detected");
      if (this.codeEle?.nativeElement) {
        this.codeEle.nativeElement.textContent = this.code;
        Prism.highlightElement(this.codeEle.nativeElement);
      }
    }
  }
}
