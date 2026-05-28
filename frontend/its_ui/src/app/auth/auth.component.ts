import { Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { EventShareService } from '../shared/services/event-share.service';
import { DatetimeService } from '../shared/services/datetime.service';
import { MarkdownDialogService } from '../shared/services/markdown-dialog.service';
import { environment } from 'src/environments/environment';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatRadioModule, MatRadioButton } from '@angular/material/radio';
import { MatCheckboxModule, MatCheckbox } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';

interface AuthResponse {
  message: string;
  token?: string;
}

@Component({
    selector: 'app-auth',
    templateUrl: './auth.component.html',
    styleUrls: ['./auth.component.css'],
    imports: [CommonModule, FormsModule, MatCardModule, MatInputModule, MatButtonModule, MatFormFieldModule, MatRadioModule, MatCheckboxModule, MatDividerModule]
})

export class AuthComponent {

  @ViewChild('consentRadioYes', {static: false}) consentRadioYes!: MatRadioButton;
  @ViewChild('consentRadioNo', {static: false}) consentRadioNo!: MatRadioButton;
  @ViewChild('privacyCheckbox', {static: false}) privacyCheckbox!: MatCheckbox;
  
  showDataTermPopup() {
    this.markdownDialogService.openDataTerms();
  }

  showPrivacyPolicyPopup() {
    this.markdownDialogService.openPrivacyPolicy();
  }

  showImprintPopup() {
    this.markdownDialogService.openImprint();
  }

  apiUrl = environment.apiUrl;
  timer: any;

  @Output() loginEvent : EventEmitter<string> = new EventEmitter<string>();
  loginStatus: string = 'none';

  currentForm: string = "login";

  constructor(
    private http: HttpClient,
    private eventShareService: EventShareService,
    private datetimeService: DatetimeService,
    private markdownDialogService: MarkdownDialogService
  ) {}

  login(username: string, password: string): void {
    const formData = new FormData()
    formData.append('username', `${username}@anonym.de`);
    formData.append('password', password);

    this.http.post<any>(`${this.apiUrl}/auth/jwt/login`, formData, { withCredentials: true}).subscribe(
      () => {
          this.loginStatus = "loggedIn";
          this.http.get<any>(`${this.apiUrl}/users/me`, {"withCredentials": true}).subscribe(
            (data)  => {
            const isVerified = data.is_verified;
            if (!isVerified){
              const verification_request_complete: boolean = this.request_verify(username, true);
              if (verification_request_complete){
                this.login(username, password);
              }
            }
            else {
          this.emitLoginEvent();
          this.timer = setTimeout(
            () => {
              this.loginStatus = 'LoggedOut';
              this.eventShareService.emitViewChange(this.loginStatus);
              alert("You have been automatically logged out, since your authentification token has expired. However you can just log back in, your progress is stored.")
            }
            , 6400000);
           this.retrieveSessionSettings();
          }
          });
      },
      error => {
        console.error('Login error:', error);
        alert("Login not successful. Please provide valid credentials and ensure a proper connection.")
      }
    );
  }

  emitLoginEvent() {
    this.loginEvent.emit(this.loginStatus);
  }

  register(email: string, username: string, password: string, dataCollectionConsent: boolean): void {
    if(!this.consentRadioNo.checked && !this.consentRadioYes.checked){
      window.alert("Please select (Yes/No) whether we can use your data for scientific purposes.")
      return;
    }

    if(!this.privacyCheckbox.checked){
      window.alert("Please acknowledge the Privacy Policy to proceed.")
      return;
    }

    const body = {"username": username,
                  "verification_email": email,
                  "email": `${username}@anonym.de`,
                  "password": password,
                  "enrolled_courses": [],
                  "current_course": "",
                  "register_datetime": this.datetimeService.datetimeNow(),
                  "settings": {"dataCollection": dataCollectionConsent}
                };
    this.http.post<AuthResponse>(`${environment.apiUrl}/auth/register`, body).subscribe(
      response => {
          this.request_verify(username, false);
      },
      error => {
        console.error('Registration error:', error);
        alert("Registration not successful. Probably the user already exists.")
      }
    );
  }

  request_verify(username: string, rerequest: boolean){
    var verification_complete = false;
      if(!rerequest){
          this.http.post<any>(`${environment.apiUrl}/auth/request-verify-token`, {"email": `${username}@anonym.de`}).subscribe()
      }
      const token = window.prompt("Please check your Emails for a verification token and enter it here:")
      this.http.post<any>(`${environment.apiUrl}/auth/verify`, {"token": token}).subscribe(
        () => {this.setForm("login");
                verification_complete = true;
        }
      )
    return verification_complete
  }

  forgotPassword(username: string, resetKey: string, verificationEmail: string)
  {
    const body = {"email": `${username}@anonym.de`,
                  "resetKey": resetKey,
                  "verificationEmail": verificationEmail
                };
    this.http.post<any>(`${this.apiUrl}/auth/forgot-password`, body, { withCredentials: true}).subscribe(
      () => {
        alert("Reset token for password reset was created and send via email.")
        this.setForm("reset-pw")
      },
      error => {
        console.error('Login error:', error);
        alert("Forgot Password not successful. Please provide valid username and reset key. The reset key was issued via email on registration. Please contact your admin if it cannot be recovered.")
      }
    );
  }

  resetPassword(password: string, resetToken: string): void
  {
    const body = {"token": resetToken,
    "password": password,
  };

    this.http.post<any>(`${this.apiUrl}/auth/reset-password`, body, { withCredentials: true}).subscribe(
      () => {
        alert("Password was reset.")
        this.setForm("login");
      },
      error => {
        console.error('Login error:', error);
        alert("Reset Password not successful. Please provide a valid reset token.")
      }
    ); 
  }

  setForm(form: string){
    this.currentForm = form;
  }

  retrieveSessionSettings() {
    this.http.get<any>(`${this.apiUrl}/users/me`, {withCredentials: true}).subscribe(
      (data) => {
        const settings = data.settings
          for (const key in settings) {
            sessionStorage.setItem(key, settings[key]);
        }
      }
    )
  }
  
}
