import { Component, AfterViewInit, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { EventShareService } from '../shared/services/event-share.service';
import { MarkdownDialogService } from '../shared/services/markdown-dialog.service';
import { environment } from 'src/environments/environment';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatListModule } from '@angular/material/list';
import { MatDividerModule } from '@angular/material/divider';

@Component({
    selector: 'app-profile',
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.css'],
    imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatCheckboxModule,
    MatListModule,
    MatDividerModule
  ]
})
export class ProfileComponent {

  dataCollectionConsent: boolean = false;

  @Output() profileAction: EventEmitter<string> = new EventEmitter<string>;

  apiUrl: string = environment.apiUrl;
  email: string = '';
  name: string = '';
  registeredDatetime: string = '';
  user: {register_datetime?: any, settings?: any, enrolled_courses?: string[], roles?: string[], username?: string, current_course?: string} = {};
  enrolledCourses: string = "";

  constructor(
    private http: HttpClient,
    private eventShareService: EventShareService,
    private markdownDialogService: MarkdownDialogService
  ) {}

  showDataTermsPopup() {
    this.markdownDialogService.openDataTerms();
  }

    ngAfterViewInit() {
      this.show_profile()
    }

    show_profile() {
      this.http.get<any>(`${this.apiUrl}/users/me`, {"withCredentials": true}).subscribe(
        (data)  => {
        this.user = {
          register_datetime: data.register_datetime,
          settings: data.settings,
          enrolled_courses: data.enrolled_courses,
          roles: data.roles,
          username: data.username,
          current_course: data.current_course
        };
        this.registeredDatetime = this.user.register_datetime["local"];
        this.enrolledCourses = this.user.enrolled_courses!.join("\n");
        this.dataCollectionConsent = this.user.settings.dataCollection || false;
      });
    }

    logout(){
      this.http.post(`${this.apiUrl}/auth/jwt/logout`,{}, {withCredentials: true}).subscribe();
      console.log("logged out!");
      this.profileAction.emit('loggedOut');
    }

    closeProfile() {
      console.log("close profile!");
      this.profileAction.emit('closedProfile');
    }

    updateSettings() {
      if(this.dataCollectionConsent !== this.user.settings.dataCollection) {
        this.user.settings.dataCollection = this.dataCollectionConsent;
        this.http.patch<any>(`${this.apiUrl}/users/me`, this.user, {withCredentials: true}).subscribe();
        sessionStorage.setItem('dataCollection', String(this.dataCollectionConsent));
      }
    }

}
