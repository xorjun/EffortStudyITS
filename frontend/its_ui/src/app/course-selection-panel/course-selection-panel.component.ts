import { Component, Output, EventEmitter } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { RolesService } from '../shared/services/roles.service';
import { EventShareService } from '../shared/services/event-share.service';

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
    this.client.post(endpoint_url, body, {withCredentials: true}).subscribe();
    this.courseSelected.emit("courseSelected");
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
      if (window.confirm("This action can overwrite existing courses and course settings. It is safer to only update tasks for existing courses."))
      {
        this.client.post<any>(url, formData,{"withCredentials": true}).subscribe(
          () => {
            console.log("Course Uploaded!")
          },
          error => {
            console.error('Upload error:', error);
            alert("A problem occured during course uploading. Please refer to logs for details.")
          }
        );
      }
    }
  }
}
