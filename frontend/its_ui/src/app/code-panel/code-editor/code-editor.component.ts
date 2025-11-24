import { Component, Output, EventEmitter, ElementRef, ViewChild, OnInit, AfterViewInit} from '@angular/core';
import { Subscription } from 'rxjs';
import { MonacoCodeEditorComponent } from 'src/app/shared/components/monaco-code-editor/monaco-code-editor.component';
import { EventShareService } from 'src/app/shared/services/event-share.service';
import { DatetimeService } from 'src/app/shared/services/datetime.service';

@Component({
  selector: 'app-code-editor',
  templateUrl: './code-editor.component.html',
  styleUrls: ['./code-editor.component.css']
})
export class CodeEditorComponent {

  @Output() codeChangeEvent : EventEmitter<string[]> = new EventEmitter<string[]>();
  language: string = "python";

  @ViewChild(MonacoCodeEditorComponent) monacoCodeEditorComponent!: MonacoCodeEditorComponent;

  timer: any; 

  newContentList: any[] = [];
  datetimeList: any[] = []
  lastSnapshot: string = "";


  //newTaskSubscription: Subscription;
  current_task_id: string = "";
  prefix: string = "";

  constructor(
    private eventShareService: EventShareService,
    private datetimeService: DatetimeService,
  ) {
/*     this.newTaskSubscription = this.eventShareService.newTaskFetched$.subscribe(() => {
        //TODO: Better control time of execution, because codePanel is also listening to newTaskFetched!
        if (typeof this.prefix !== 'undefined') {
          this.prefix = sessionStorage.getItem('taskPrefix')!;
        }
        else {
          this.codeChangeEvent.emit(this.userContentControl);
          this.prefix = sessionStorage.getItem('taskPrefix')!;
        }
    }); */
  }

  // Provide editor content
  get contentControl(): string {
    //const content: any = this.form.get('content')?.value;
    const content: any = this.monacoCodeEditorComponent.getContent();
    return content != null ? content : '';
  }
  
  get userContentControl() {
    const content: any = this.monacoCodeEditorComponent.getContent();
    if (content.startsWith(this.prefix)) {
      return content.slice(this.prefix.length);
    }
    else {
     console.error("Code prefix not present!") 
    }
  }

  //Set Editor Content
  setEditorContent(value: string) {
    this. monacoCodeEditorComponent.setContent(value);
  }

  appendContent(newContent: any){
    this.newContentList.push(newContent);
    this.datetimeList.push(this.datetimeService.datetimeNowUTC());
  }

  clearContentList(){
    this.newContentList = [];
    this.datetimeList = [];
  }

  onEditorContentChange(event: Event){
    const prefix = this.prefix;
    const newContent = this.contentControl;
    if (newContent.startsWith(prefix)) {
      var diff = newContent.slice(prefix.length);
      diff = this.deriveDiff(this.lastSnapshot , diff);
      if (diff.length > 0){
        this.lastSnapshot = newContent.slice(prefix.length);
        //this.newContentList.push(diff);
        this.appendContent(diff);
      }
      clearTimeout(this.timer);
      this.emitCodeChangeEventTimer();
    }
    this.ensurePrefix(newContent);
  }

  private ensurePrefix(newContent: string){
    const prefix = this.prefix;
    if(!(newContent.startsWith(prefix))) {
      console.log("Ensuring prefix");
      newContent = prefix + newContent.slice(prefix.length + 1);
      this.setEditorContent(newContent);
    }
    return(newContent);
  }


    private deriveDiff(oldSnapshot: string, newSnapshot: string) : any {
      const lines_old = oldSnapshot.split("\n");
      const lines_new = newSnapshot.split("\n");
      const n_old = lines_old.length;
      const n_new = lines_new.length;
      if (n_new != n_old){
        return [[-1, newSnapshot]]
      }
      const n = Math.max(n_old, n_new);
      var diff: any[] = []
      for (let i = 0; i < n; i++){
        if (lines_old[i] != lines_new[i]){
          diff.push([i+1, lines_new[i]]);
          if (diff.length > 1) {
            diff = [[-1, newSnapshot]];
            return diff
          }
        }
      }
      return diff
  }

  // The Timer is set every time the user code changes, if it changes again,
  // the timer is reset
  emitCodeChangeEventTimer() {
    this.timer = setTimeout(
      () => {
        const prefix = this.prefix;
        //if (newVal.startsWith(prefix)) {
          this.codeChangeEvent.emit(this.newContentList);
          //this.newContentList = [];
          this.clearContentList();
        //}
      }
    , 1500) //Milliseconds timeout
  }

  ngOnDestroy() {
    //this.newTaskSubscription.unsubscribe();
  }

}
