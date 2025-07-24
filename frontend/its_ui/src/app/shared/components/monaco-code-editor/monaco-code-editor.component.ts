import { Component, AfterViewInit, ElementRef, ViewChild, Input, HostListener, Output, EventEmitter } from '@angular/core';
import { MonacoEditorService } from '../../services/monaco-edito-service.service';
import { first } from 'rxjs';
import themeJson from '../monaco-code-editor/Tomorrow-LightNight.json'

declare var monaco: any;

//Source for prefix-feature
//https://stackoverflow.com/questions/46982692/monaco-editor-how-to-make-some-areas-readonly

@Component({
  selector: 'app-monaco-code-editor',
  templateUrl: './monaco-code-editor.component.html',
  styleUrls: ['./monaco-code-editor.component.css']
})
export class MonacoCodeEditorComponent implements AfterViewInit {


  @Input() language: string = "";
  @ViewChild("fontMeasure", {static: true}) fontMeasure!: ElementRef
  fontSize?: string;

  @Output() contentChangeEvent : EventEmitter<any> = new EventEmitter();

  constructor(private monacoEditorService: MonacoEditorService){
    monacoEditorService.load();
  }

  public _editor: any;
  @ViewChild('editorContainer', { static: true })_editorContainer!: ElementRef;

  private initMonaco(): void {
    if(!this.monacoEditorService.loaded) {
      this.monacoEditorService.loadingFinished.pipe(first()).subscribe(() => {
        this.initMonaco();
      });
      return;
    }

    // Define custom theme
    monaco.editor.defineTheme('tomorrow-light-night', themeJson);


/*     monaco.editor.defineTheme('its-grey', {
      base: 'tomorrow-night',
      inherit: true,
      rules: [],
      colors: {
          'editor.background': '#2d2d2d',
      },
  }); */

    this._editor = monaco.editor.create(
      this._editorContainer.nativeElement,
      {"theme": "tomorrow-light-night",
        "language": this.language,
        "fontSize": this.fontMeasure.nativeElement.getBoundingClientRect().height,
        "padding": {"top": 10},
        minimap: { enabled: false },
        automaticLayout: true,
      }
    );
    this.subscribeToChanges();
  }

  ngAfterViewInit(): void {
    this.initMonaco();
  }

  subscribeToChanges(){
    this._editor.onDidChangeModelContent(() => {
      this.contentChangeEvent.emit("content changed!")
    })
  }

  //Update monaco view
  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    if (this._editor != undefined) {
      this.updateMonaco();
      }
    }

  private updateMonaco(){
    this._editor.updateOptions( {
    "language": this.language,
    "fontSize": this.fontMeasure.nativeElement.getBoundingClientRect().height,
  })
  }

  //Interact with Monaco content
  getContent(){
    if (this._editor != undefined)
      {
        return this._editor.getValue();
      }
    else {
      setTimeout(() => {
        return this.getContent();
      }, 50)
    }
  }

  setContent(value: string){
    if (this._editor != undefined)
      {
        this._editor.setValue(value);
      }
    //wait for editor to be initialized
    else {
      setTimeout(() => {
        this.setContent(value);
      },50)
    }
  }
}