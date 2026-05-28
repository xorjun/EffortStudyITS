import { Component, Renderer2,  AfterViewChecked, AfterViewInit, ElementRef, OnDestroy, OnInit, ViewChild, EventEmitter, Output, HostListener, ViewChildren, QueryList } from '@angular/core';
import { CommonModule } from '@angular/common';

//Prism
import { FormBuilder, ReactiveFormsModule } from '@angular/forms'
import { fromEvent, Subscription } from 'rxjs';
import { PrismHighlightService } from 'src/app/shared/services/prism-highlight.service'

import { EventShareService } from 'src/app/shared/services/event-share.service';
import { MatCheckbox, MatCheckboxChange, MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-multiple-choice',
    templateUrl: './multiple-choice.component.html',
    styleUrls: ['./multiple-choice.component.css'],
    imports: [CommonModule, ReactiveFormsModule, MatCheckboxModule, MatTooltipModule, MatIconModule]
})
export class MultipleChoiceComponent {

  checked: string[] = [];
  choices: string[] = [];
  @ViewChildren ('checkBox') checkBox?: QueryList<MatCheckbox>;

  newTaskSubscription: Subscription;
  current_task_id: string = "";

  constructor(
    private eventShareService: EventShareService,
  ) {
    this.newTaskSubscription = this.eventShareService.newTaskFetched$.subscribe(() => {
      this.choices = [];
      //TODO: trigger an attempt-log to register start time!
    });
  }

  ngOnInit(): void {
  }

  ngOnDestroy() {
    this.newTaskSubscription.unsubscribe();
  }

  getCheckbox(checkbox: MatCheckbox) {
    this.checked = []; // resetting each Time new event is fired.

    if(!this.checkBox) return;

    // filtering only checked values and assign to checked variable.
    const checked = this.checkBox.filter(checkbox => checkbox.checked);

    checked.forEach(data => {
      this.checked.push(data.value);
    });
  }

}
