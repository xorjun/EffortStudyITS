import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Observable, tap } from 'rxjs';


@Injectable({
  providedIn: 'root'
})

export class CourseSettingsService {

  course: any;

  constructor(private client: HttpClient) { 
    if (sessionStorage.getItem("courseName") != undefined)
      {
        this.fetchCourse();
      }
  }

  fetchCourse(): Observable<any> {
    const courseID = sessionStorage.getItem("courseID");
    const url = `${environment.apiUrl}/course/get/${courseID}`;
    return this.client.get(url, { withCredentials: true });
  }

  // Additional method to set course after fetching
  getCourse(): Observable<any> {
    return this.fetchCourse().pipe(
      tap(data => this.course = data)
    );
  }
}
