import { Component, EventEmitter, Output, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormControl} from '@angular/forms';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-course-settings',
  templateUrl: './course-settings.component.html',
  styleUrls: ['./course-settings.component.css']
})
export class CourseSettingsComponent {

  @Output() settingsClosedEvent: EventEmitter<string> = new EventEmitter<string>

  settingsForm!: FormGroup;
  formGroupArray: FormGroup[] = [];

  course: any = {};
  courseSettingsList!: any[];

  constructor(private client: HttpClient){
    this.settingsForm = new FormGroup({
      pedagogical_model: new FormControl("default"),
      language_generation_model: new FormControl("default"),
      sample_settings: new FormControl([]),
      feedback_init_time: new FormControl(0),
      feedback_cooldown: new FormControl(0),
    });
  }

  ngOnInit(){
    const course_id = sessionStorage.getItem("courseID");
    this.client.get<any>(`${environment.apiUrl}/course/get_settings/${course_id}`, {"withCredentials": true}).subscribe(
      (data) => {
        this.course = data
        this.courseSettingsList = data.course_settings_list;
        this.settingsForm.patchValue({
          pedagogical_model: this.course.course_settings_list[0].pedagogical_model,
          language_generation_model: this.course.course_settings_list[0].language_generation_model,
          sample_settings: this.course["sample_settings"].join(','),
          feedback_init_time: +this.courseSettingsList[0].feedback_init_time,
          feedback_cooldown: +this.courseSettingsList[0].feedback_cooldown,
        });
        this.initializeFormGroupArray();
      }
    );
  }

  saveSettings(): void {
    const course_id = this.course["id"];
    //var data = this.settingsForm.value;
    var settingsList: any[] = [this.settingsForm.value];
    this.course["sample_settings"] = settingsList[0]["sample_settings"].split(",").map((i: string) => Number(i));
    delete settingsList[0]["sample_settings"];
    for (let index = 0; index < this.formGroupArray.length; index++) {
      settingsList[index+1] = this.formGroupArray[index].value;
    }
    settingsList[0]["course_id"] = course_id
    this.course["course_settings_list"] = settingsList
    //data.course_id = course_id;
    this.client.post<any>(`${environment.apiUrl}/course/update_settings`, this.course, {"withCredentials": true}).subscribe();
  }

  closeSettings(): void {
    this.settingsClosedEvent.emit("settingsClosed")
  }

  addNewAlternativeSetting() {
    this.course["sample_settings"].push(0);
    this.settingsForm.patchValue({"sample_settings": this.course["sample_settings"].join(",")});
    this.courseSettingsList.push({});
    this.formGroupArray.push(new FormGroup({}));
    }

  updateActiveSettings(settingsIndex: number, setting: string) {
    const defaultValue = this.courseSettingsList[0][setting];
    this.formGroupArray[settingsIndex-1].addControl(setting, new FormControl(defaultValue));
    this.courseSettingsList[settingsIndex][setting] = defaultValue;
  }

  getActiveSettings(settingsIndex: number) {
    return Object.keys(this.courseSettingsList[settingsIndex]);
  }

  initializeFormGroupArray() {
    this.formGroupArray = []
    for (let index = 1; index < this.courseSettingsList.length; index++) {
      this.formGroupArray.push(new FormGroup({}));
      //TODO: Configure Formgroup
      const settings: any[] = Object.keys(this.courseSettingsList[index]);
      settings.forEach((setting) => {
        const settingValue = this.courseSettingsList[index][setting]
        this.formGroupArray[index-1].addControl(setting, new FormControl(settingValue));
      })
    }
  }

  getFormGroup(settingsIndex: number){
    return this.formGroupArray[settingsIndex-1];
  }

  resetSelection(event: Event){
    const selectElement = event.target as HTMLSelectElement;
    selectElement.selectedIndex = 0;
  }

  deleteAlternativeSetting(index: number){
    this.course["sample_settings"].splice(index, 1)
    if (this.course["sample_settings"].length == 1){
      this.course["sample_settings"][0] = 1
    }
    this.settingsForm.patchValue({"sample_settings": this.course["sample_settings"].join(",")});
    this.courseSettingsList.splice(index, 1);
    this.formGroupArray.splice(index-1, 1);
  }

  onTaskFolderSelected(input: HTMLInputElement) {
    const file: File | undefined = input.files![0];
    if (file)
    {
      const formData = new FormData();
      formData.append("file", file);
      const url: string = `${environment.apiUrl}/course/update_tasks`;
      this.client.post<any>(url, formData,{"withCredentials": true}).subscribe(
        () => {
          console.log("Tasks updated!")
        },
        error => {
          console.error('Upload error:', error);
          alert("A problem occured during task uploading. Please refer to logs for details.")
        }
      );
    }
  }

}
