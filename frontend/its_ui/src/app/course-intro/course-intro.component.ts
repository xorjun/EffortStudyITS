import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CourseSettingsService } from '../shared/services/course-settings-service.service';
import { MarkdownPanelComponent } from '../shared/components/markdown-panel/markdown-panel.component';

@Component({
    selector: 'app-course-intro',
    templateUrl: './course-intro.component.html',
    styleUrls: ['./course-intro.component.css'],
    imports: [CommonModule, MarkdownPanelComponent, MatButtonModule, MatIconModule]
})
export class CourseIntroComponent implements OnInit {
  @Output() introCompleted = new EventEmitter<string>();

  introduction: string = '';
  courseDisplayName: string = '';

  constructor(private courseSettingsService: CourseSettingsService) {}

  ngOnInit(): void {
    this.courseSettingsService.getCourse().subscribe((course: any) => {
      this.introduction = course.introduction || '';
      this.courseDisplayName = course.display_name || '';
    });
  }

  startCourse(): void {
    this.introCompleted.emit('introCompleted');
  }
}
