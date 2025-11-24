import { Component, Output, EventEmitter } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { RolesService } from '../shared/services/roles.service';
import { EventShareService } from '../shared/services/event-share.service';
import { MatCheckboxChange } from '@angular/material/checkbox';

export interface CourseDescription{
  unique_name: string;
  display_name: string;
}
@Component({
  selector: 'app-course-selection-panel',
  templateUrl: './course-selection-panel.component.html',
  styleUrls: ['./course-selection-panel.component.css']
})
export class CourseSelectionPanelComponent {
  @Output() courseSelected: EventEmitter<string> = new EventEmitter<string>;

  courses: CourseDescription[] = [];
  course_names: string[] =  [];
  roles: string[] = [];
  upload_overwrite: boolean = false;

  constructor(
      private client: HttpClient,
      private rolesService: RolesService,
      private eventShareService: EventShareService,
    ){
      rolesService.getRoles().subscribe((roles) => {
        this.roles = roles.roles;
      });
    }

  selectCourse(courseID: string){
    sessionStorage.setItem("courseID", courseID);
    const endpoint_url = `${environment.apiUrl}/course/select`;
    const body = {
      'course_unique_name': courseID};
    this.client.post(endpoint_url, body, {withCredentials: true}).subscribe(() => {
      this.courseSelected.emit("courseSelected");
    }
    );
  }

  ngOnInit(): void {
    this.fetchCourseInfo()
  }

  fetchCourseInfo(){
    const endpoint_url = `${environment.apiUrl}/course/info/`;
    this.client.get<any>(endpoint_url, {withCredentials: true}).subscribe((data) => { 
      this.courses =  data.course_list;
  });
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
          } else {
            console.log("Course rejected!")
          }
          if (data.headers.get("warning") != null) {
            alert("Warning: " + data.headers.get("warning"))
          }
        },
        error => {
          console.error('Upload error:', error);
          alert("A problem occured during course uploading. Please refer to logs for details.")
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
