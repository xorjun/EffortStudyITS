import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { RolesService } from '../shared/services/roles.service';
import { EventShareService } from '../shared/services/event-share.service';
import { MatCheckboxChange, MatCheckboxModule } from '@angular/material/checkbox';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatListModule } from '@angular/material/list';
import { MatCardModule } from '@angular/material/card';
import { FormsModule } from '@angular/forms';
import { StudyTelemetryService } from '../shared/services/study-telemetry.service';

export interface CourseDescription{
  unique_name: string;
  display_name: string;
}

@Component({
    selector: 'app-course-selection-panel',
    templateUrl: './course-selection-panel.component.html',
    styleUrls: ['./course-selection-panel.component.css'],
    imports: [CommonModule, MatCheckboxModule, MatInputModule, MatButtonModule, MatIconModule, MatDividerModule, MatTooltipModule, MatListModule, MatCardModule, FormsModule]
})
export class CourseSelectionPanelComponent {
  @Output() courseSelected: EventEmitter<string> = new EventEmitter<string>;

  availableCourses: CourseDescription[] = [];
  enrolledCourses: CourseDescription[] = [];
  filteredAvailableCourses: CourseDescription[] = [];
  course_names: string[] =  [];
  roles: string[] = [];
  upload_overwrite: boolean = false;
  searchQuery: string = '';

  constructor(
      private client: HttpClient,
      private rolesService: RolesService,
      private eventShareService: EventShareService,
      private studyTelemetryService: StudyTelemetryService,
    ){
        sessionStorage.setItem('livePreviewMode', 'false');
      rolesService.getRoles().subscribe((roles) => {
          this.roles = roles.roles || [];
          this.syncLivePreviewMode();
      });
    }

    private syncLivePreviewMode(afterSync?: () => void): void {
      if (!this.roles.includes('admin')) {
        sessionStorage.setItem('livePreviewMode', 'false');
        afterSync?.();
        return;
      }

      this.client.get<any>(`${environment.apiUrl}/settings/get`, { withCredentials: true }).subscribe({
        next: (data) => {
          sessionStorage.setItem('livePreviewMode', String(!!data.live_preview_mode));
          afterSync?.();
        },
        error: () => {
          sessionStorage.setItem('livePreviewMode', 'false');
          afterSync?.();
        },
      });
    }

  selectCourse(courseID: string){
      const openCourse = () => {
        sessionStorage.setItem("courseID", courseID);
        this.studyTelemetryService.logEvent('course-select', {
          courseId: courseID,
        });
        const endpoint_url = `${environment.apiUrl}/course/select`;
        const body = {
          'course_unique_name': courseID};
        this.client.post(endpoint_url, body, {withCredentials: true}).subscribe(() => {
          this.courseSelected.emit("courseSelected");
        }
        );
      };

      if (this.roles.length === 0) {
        this.rolesService.getRoles().subscribe((roles) => {
          this.roles = roles.roles || [];
          this.syncLivePreviewMode(openCourse);
        });
        return;
      }

      this.syncLivePreviewMode(openCourse);
  }

  ngOnInit(): void {
    this.fetchAvailableCourses();
    this.fetchEnrolledCourses();
  }

  fetchAvailableCourses(){
    const endpoint_url = `${environment.apiUrl}/course/info`;
    this.client.get<any>(endpoint_url, {withCredentials: true}).subscribe((data) => { 
      this.availableCourses = (data.course_list || []).sort((a: CourseDescription, b: CourseDescription) => 
        a.display_name.localeCompare(b.display_name)
      );
      this.filterCourses();
    });
  }

  fetchEnrolledCourses(){
    const endpoint_url = `${environment.apiUrl}/course/enrolled_courses`;
    this.client.get<any>(endpoint_url, {withCredentials: true}).subscribe((data) => { 
      this.enrolledCourses = (data.course_list || []).sort((a: CourseDescription, b: CourseDescription) => 
        a.display_name.localeCompare(b.display_name)
      );
    });
  }

  enrollInCourse(courseUniqueName: string){
    console.log("Enrolling")
    this.studyTelemetryService.logEvent('course-enroll', {
      courseId: courseUniqueName,
    });
    const endpoint_url = `${environment.apiUrl}/course/enroll/${courseUniqueName}`;
    this.client.put(endpoint_url, {}, {withCredentials: true}).subscribe(() => {
      this.selectCourse(courseUniqueName);
    });
  }

  filterCourses(){
    if (!this.searchQuery) {
      this.filteredAvailableCourses = this.availableCourses;
    } else {
      const query = this.searchQuery.toLowerCase();
      this.filteredAvailableCourses = this.availableCourses.filter(course => 
        course.display_name.toLowerCase().includes(query) || 
        course.unique_name.toLowerCase().includes(query)
      );
    }
  }

  onSearchChange(){
    this.filterCourses();
  }

  onCourseFolderSelected(input: HTMLInputElement) {
    const file: File | undefined = input.files![0];
    if (file)
    {
      const formData = new FormData();
      formData.append("file", file);
      const url: string = `${environment.apiUrl}/course/upload_course`;
      var params = {"overwrite": this.upload_overwrite}
      this.client.post<any>(url, formData, {"withCredentials": true, params: params, observe: 'response'}).subscribe(
        data => {
          if (data.status == 200) {
            console.log("Course uploaded.")
            // Refresh course lists to show newly uploaded course
            this.fetchAvailableCourses();
            this.fetchEnrolledCourses();
          } else {
            console.log("Course rejected!")
          }
          if (data.headers.get("warning") != null) {
            alert("Warning: " + data.headers.get("warning"))
          }
        },
        error => {
          console.error('Upload error:', error);
          alert("A problem occured during course uploading:\n\n" + error.error.detail)
        }
      );
    }
  }

  onForceUpload(event: MatCheckboxChange) {
    if (!this.upload_overwrite) {
      if (window.confirm(
          "This action can irreversably overwrite course settings and parameters (such as from a trained PFA model).\n\nTHIS WILL OVERWRITE YOUR USER-GROUP ASSIGNMENTS!")) {
        this.upload_overwrite = true;
      } else {
        this.upload_overwrite = false
      }
    } else {
      this.upload_overwrite = !this.upload_overwrite
    }

    event.source.checked = this.upload_overwrite;
  }
}
