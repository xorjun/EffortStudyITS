import { Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EventShareService } from '../shared/services/event-share.service';
import { DatetimeService } from '../shared/services/datetime.service';

import { environment } from 'src/environments/environment';
import { DataTermsPopupComponent } from '../shared/components/data-terms-popup/data-terms-popup.component';
import { PrivacyPolicyPopupComponent } from '../shared/components/privacy-policy-popup/privacy-policy-popup.component'
import { timeout } from 'rxjs';

interface AuthResponse {
  message: string;
  token?: string;
}

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})

export class AuthComponent {

  @ViewChild('dataTermsPopupComponent', {static: false}) dataTermsPopupComponent!: DataTermsPopupComponent;
  @ViewChild('privacyPolicyPopupComponent', {static: false}) privacyPolicyPopupComponent!: PrivacyPolicyPopupComponent;
  @ViewChild('consentCheckboxYes', {static: false}) consentCheckboxYes!: ElementRef;
  @ViewChild('consentCheckboxNo', {static: false}) consentCheckboxNo!: ElementRef;
  @ViewChild('privacyCheckbox', {static: false}) privacyCheckbox!: ElementRef;
  
  //showDataTermPopup: boolean = false;
  showDataTermPopup() {
    this.dataTermsPopupComponent!.showPopup();
  }

  showPrivacyPolicyPopup() {
    this.privacyPolicyPopupComponent!.showPopup();
  }

  apiUrl = environment.apiUrl;
  timer: any;

  @Output() loginEvent : EventEmitter<string> = new EventEmitter<string>();
  loginStatus: string = 'none';

  currentForm: string = "login";

  constructor(private http: HttpClient,
              private eventShareService: EventShareService,
              private datetimeService: DatetimeService) {}

  login(username: string, password: string): void {
    // unfortunatley, the fastapi-users package requres logins to be FormData and not JSON.
    const formData = new FormData()
    formData.append('username', `${username}@anonym.de`); //At some later point we may want to prefer e-mail based login
    formData.append('password', password);

    this.http.post<any>(`${this.apiUrl}/auth/jwt/login`, formData, { withCredentials: true}).subscribe(
      () => {
          // Handle successful login
          this.loginStatus = "loggedIn";
          //Find if user is verified.
          this.http.get<any>(`${this.apiUrl}/users/me`, {"withCredentials": true}).subscribe(
            (data)  => {
            const isVerified = data.is_verified;
            if (!isVerified){
              const verification_request_complete: boolean = this.request_verify(username);
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
    if(!this.consentCheckboxNo.nativeElement.checked && !this.consentCheckboxYes.nativeElement.checked){
      window.alert("Please select (Yes/No) whether we can use your data for scientific purposes.")
      return;
    }

    if(!this.privacyCheckbox.nativeElement.checked){
      window.alert("Please acknowledge the Privacy Policy to proceed.")
      return;
    }

    const body = {"username": username,
                  "verification_email": email,
                  // email has to be a "dummy" as of the requirements of the fastapi-users module.
                  "email": `${username}@anonym.de`,
                  "password": password,
                  "enrolled_courses": [],
                  "current_course": "",
                  "register_datetime": this.datetimeService.datetimeNow(),
                  "settings": {"dataCollection": dataCollectionConsent}
                };
    this.http.post<AuthResponse>(`${environment.apiUrl}/auth/register`, body).subscribe(
      response => {
          // Handle successful registration
          this.request_verify(username);
      },
      error => {
        console.error('Registration error:', error);
        alert("Registration not successful. Probably the user already exists.")
      }
    );
  }

  request_verify(username: string){
    var verification_complete = false;
      this.http.post<any>(`${environment.apiUrl}/auth/request-verify-token`, {"email": `${username}@anonym.de`}).subscribe()
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
        //for (var key in Object.keys(settings)) {
          for (const key in settings) {
            sessionStorage.setItem(key, settings[key]);
        }
      }
    )
  }
  
}
