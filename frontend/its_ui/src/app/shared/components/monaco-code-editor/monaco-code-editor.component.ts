import { Component, AfterViewInit, ElementRef, ViewChild, Input, HostListener, Output, EventEmitter, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonacoEditorService } from '../../services/monaco-edito-service.service';
import { first } from 'rxjs';
import themeJson from '../monaco-code-editor/Tomorrow-LightNight.json'

declare var monaco: any;

export interface AdditionalFile {
  name: string;
  content: string;
  language: string;
  readOnly: boolean;
}

@Component({
  selector: 'app-monaco-code-editor',
  templateUrl: './monaco-code-editor.component.html',
  styleUrls: ['./monaco-code-editor.component.css'],
  standalone: true,
  imports: [CommonModule]
})
export class MonacoCodeEditorComponent implements AfterViewInit, OnChanges {


  @Input() language: string = "";
  @Input() additionalFiles: AdditionalFile[] = [];
  @Input() clipboardLocked: boolean = false;
  @ViewChild("fontMeasure", {static: true}) fontMeasure!: ElementRef
  fontSize?: string;

  @Output() contentChangeEvent : EventEmitter<any> = new EventEmitter();
  @Output() clipboardTelemetryEvent: EventEmitter<{ action: string, blocked: boolean }> = new EventEmitter();

  constructor(private monacoEditorService: MonacoEditorService){
    monacoEditorService.load();
  }

  public _editor: any;
  @ViewChild('editorContainer', { static: true })_editorContainer!: ElementRef;

  private models: Map<string, any> = new Map();
  private modelSubscriptions: Map<string, any> = new Map();
  public currentFileName: string = '';
  public mainFileName: string = 'main.py';
  private mainModel: any;
  private pendingTaskReset: boolean = false;
  private pendingTaskId: string = '';
  private editorChangeSubscription: any;
  private editorDomNode: HTMLElement | null = null;
  private lastClipboardTelemetry: { signature: string, timestamp: number } | null = null;

  private readonly clipboardEventHandler = (event: ClipboardEvent) => {
    this.emitClipboardTelemetry(event.type, this.clipboardLocked);
    if (!this.clipboardLocked) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
  };

  private readonly keydownEventHandler = (event: KeyboardEvent) => {
    const action = this.getClipboardActionFromShortcut(event);
    if (!this.clipboardLocked || action === null) {
      return;
    }
    this.emitClipboardTelemetry(action, true);
    event.preventDefault();
    event.stopPropagation();
  };

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
    this.attachClipboardGuards();
    this.attachMonacoClipboardOverrides();
    this.createMainModel('main');
    this.setupAdditionalFiles();
    this.subscribeToEditorChanges();
    if (this.pendingTaskReset) {
      this.pendingTaskReset = false;
      const taskId = this.pendingTaskId;
      this.pendingTaskId = '';
      this.resetForNewTask(taskId);
    }
  }

  ngAfterViewInit(): void {
    this.initMonaco();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['additionalFiles'] && this._editor) {
      this.setupAdditionalFiles();
    }
  }

  ngOnDestroy(): void {
    this.removeClipboardGuards();
    this.disposeModels();
    if (this._editor) {
      this._editor.dispose();
      this._editor = null;
    }
  }

  private setupAdditionalFiles(): void {
    if (!this._editor || !this.additionalFiles) return;

    this.additionalFiles.forEach(file => {
      if (!this.models.has(file.name)) {
        const uri = monaco.Uri.parse(`file:///${Date.now()}_${file.name}`);
        const model = monaco.editor.createModel(file.content, file.language, uri);
        this.models.set(file.name, model);
      }
    });
  }

  private createMainModel(taskId: string): void {
    const mainContent = this._editor.getValue();
    this._editor.setValue('');
    this.mainFileName = `${taskId}.py`;
    const uri = monaco.Uri.parse(`file:///${Date.now()}_${this.mainFileName}`);
    this.mainModel = monaco.editor.createModel(mainContent, this.language, uri);
    this.models.set(this.mainFileName, this.mainModel);
    this._editor.setModel(this.mainModel);
    this.currentFileName = this.mainFileName;
  }

  private attachMonacoClipboardOverrides(): void {
    // Paste: Ctrl+V and Shift+Insert
    const pasteKbs = [
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV,
      monaco.KeyMod.Shift   | monaco.KeyCode.Insert,
    ];
    // Copy: Ctrl+C and Ctrl+Insert
    const copyKbs = [
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC,
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.Insert,
    ];
    // Cut: Ctrl+X and Shift+Delete
    const cutKbs = [
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX,
      monaco.KeyMod.Shift   | monaco.KeyCode.Delete,
    ];

    pasteKbs.forEach(kb => this._editor.addCommand(kb, () => {
      if (this.clipboardLocked) { this.emitClipboardTelemetry('paste', true); return; }
      this._editor.trigger('keyboard', 'editor.action.clipboardPasteAction', {});
    }));

    copyKbs.forEach(kb => this._editor.addCommand(kb, () => {
      if (this.clipboardLocked) { this.emitClipboardTelemetry('copy', true); return; }
      this._editor.trigger('keyboard', 'editor.action.clipboardCopyAction', {});
    }));

    cutKbs.forEach(kb => this._editor.addCommand(kb, () => {
      if (this.clipboardLocked) { this.emitClipboardTelemetry('cut', true); return; }
      this._editor.trigger('keyboard', 'editor.action.clipboardCutAction', {});
    }));

    // Safety net for right-click context menu paste: undo immediately if locked.
    this._editor.onDidPaste(() => {
      if (!this.clipboardLocked) { return; }
      this._editor.trigger('source', 'undo', {});
      this.emitClipboardTelemetry('paste', true);
    });
  }

  private attachClipboardGuards(): void {
    const domNode = this._editor?.getDomNode?.();
    if (!domNode || this.editorDomNode === domNode) {
      return;
    }

    this.removeClipboardGuards();
    domNode.addEventListener('copy', this.clipboardEventHandler);
    domNode.addEventListener('cut', this.clipboardEventHandler);
    domNode.addEventListener('paste', this.clipboardEventHandler);
    domNode.addEventListener('keydown', this.keydownEventHandler, true);
    this.editorDomNode = domNode;
  }

  private removeClipboardGuards(): void {
    if (!this.editorDomNode) {
      return;
    }
    this.editorDomNode.removeEventListener('copy', this.clipboardEventHandler);
    this.editorDomNode.removeEventListener('cut', this.clipboardEventHandler);
    this.editorDomNode.removeEventListener('paste', this.clipboardEventHandler);
    this.editorDomNode.removeEventListener('keydown', this.keydownEventHandler, true);
    this.editorDomNode = null;
  }

  private getClipboardActionFromShortcut(event: KeyboardEvent): string | null {
    const key = event.key.toLowerCase();
    const usesModifier = event.ctrlKey || event.metaKey;

    if (usesModifier && key === 'c') {
      return 'copy';
    }
    if (usesModifier && key === 'v') {
      return 'paste';
    }
    if (usesModifier && key === 'x') {
      return 'cut';
    }
    if (usesModifier && key === 'insert') {
      return 'copy';
    }
    if (event.shiftKey && key === 'insert') {
      return 'paste';
    }
    if (event.shiftKey && key === 'delete') {
      return 'cut';
    }
    return null;
  }

  private emitClipboardTelemetry(action: string, blocked: boolean): void {
    const timestamp = Date.now();
    const signature = `${action}:${blocked}`;
    if (this.lastClipboardTelemetry && this.lastClipboardTelemetry.signature === signature && timestamp - this.lastClipboardTelemetry.timestamp < 75) {
      return;
    }
    this.lastClipboardTelemetry = { signature, timestamp };
    this.clipboardTelemetryEvent.emit({ action, blocked });
  }

  private subscribeToEditorChanges(): void {
    if (this.editorChangeSubscription) {
      this.editorChangeSubscription.dispose();
    }
    this.editorChangeSubscription = this._editor.onDidChangeModelContent(() => {
      const currentModel = this._editor.getModel();
      let changedFile: string | null = null;
      
      this.models.forEach((model, fileName) => {
        if (model === currentModel) {
          changedFile = fileName;
        }
      });
      
      if (changedFile) {
        const fileConfig = this.additionalFiles.find(f => f.name === changedFile);
        if (!fileConfig?.readOnly) {
          this.contentChangeEvent.emit({ file: changedFile, changed: true });
        }
      }
    });
  }

  switchToFile(fileName: string): void {
    const model = this.models.get(fileName);
    if (model && this._editor) {
      this._editor.setModel(model);
      this.currentFileName = fileName;
      const fileConfig = this.additionalFiles.find(f => f.name === fileName);
      if (fileConfig?.readOnly) {
        this._editor.updateOptions({ readOnly: true });
      } else {
        this._editor.updateOptions({ readOnly: false });
      }
    }
  }

  disposeModels(): void {
    if (this.editorChangeSubscription) {
      this.editorChangeSubscription.dispose();
      this.editorChangeSubscription = null;
    }
    this.models.forEach((model) => model.dispose());
    this.models.clear();
    this.mainModel = null;
  }

  resetForNewTask(taskId: string): void {
    if (!this._editor) {
      this.pendingTaskReset = true;
      this.pendingTaskId = taskId;
      return;
    }
    this.disposeModels();
    this.createMainModel(taskId);
    this.setupAdditionalFiles();
    this.subscribeToEditorChanges();
    this.currentFileName = this.mainFileName;
    this._editor.setModel(this.mainModel);
    this._editor.updateOptions({ readOnly: false });
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