import { Component, Input, ViewChild, ElementRef } from '@angular/core';
import { PrismHighlightService } from '../../services/prism-highlight.service';

@Component({
  selector: 'app-markdown-panel',
  templateUrl: './markdown-panel.component.html',
  styleUrls: ['./markdown-panel.component.css']
})
export class MarkdownPanelComponent {
  @Input() markdownString: string="";
  @ViewChild("markdownContainer", {static: true}) markdownContainer!: ElementRef;


  constructor(private prismService: PrismHighlightService){
    prismService.highlightAll();
  }

  resetScroll(){
    this.markdownContainer.nativeElement.scrollTop = 0;
  }
}