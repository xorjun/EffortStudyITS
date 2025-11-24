import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-admin-settings',
  templateUrl: './admin-settings.component.html',
  styleUrls: ['./admin-settings.component.css']
})
export class AdminSettingsComponent {

  @Output() settingsClosedEvent: EventEmitter<string> = new EventEmitter<string>

  settingsForm!: FormGroup;

  constructor(private client: HttpClient){
    this.settingsForm = new FormGroup({
      api_type: new FormControl(""),
      api_url: new FormControl(""),
      api_key: new FormControl(""),
      email_whitelist: new FormControl(""),
    });
  }

  ngOnInit() {
    this.client.get<any>(`${environment.apiUrl}/settings/get`, {"withCredentials": true}).subscribe(
      (data) => {
        this.settingsForm.patchValue({
          api_type: data.api_type,
          api_url: data.api_url,
          api_key: data.api_key,
          email_whitelist: data.email_whitelist.join(","),
        });
      }
    );
  }

  saveSettings(): void {
    var settings: any = this.settingsForm.value;
    settings["email_whitelist"] = settings["email_whitelist"].split(",");
    this.client.post<any>(`${environment.apiUrl}/settings/update`, settings, {"withCredentials": true}).subscribe();
  }

  closeSettings(): void {
    this.settingsClosedEvent.emit("settingsClosed")
  }

}
