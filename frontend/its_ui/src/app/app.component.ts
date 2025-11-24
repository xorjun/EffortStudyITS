import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { EventShareService } from './shared/services/event-share.service';
import { environment } from 'src/environments/environment';
import { CourseSettingsService } from './shared/services/course-settings-service.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  title = 'Tutoring System for Programming';
  pageName = 'loginView'
  originPage = ''
  initTask?: string | null;
  course?: any

  constructor(private client: HttpClient,
    private eventShareService: EventShareService,
    private courseSettingsService: CourseSettingsService){
      eventShareService.viewChange$.subscribe(
        (status) => {
          this.setView(status);
        }
      );
  }

  ngOnInit(): void {
    this.client.get<any>(`${environment.apiUrl}/status`).subscribe((data) =>  {
      console.log(data["message"]);
    });
  }

  //TODO: Make origin-page a stack in order to enable navigating through navbar. 
  setView(status: string) {
    switch (status) {
      case 'loggedIn':
          this.pageName = 'welcomePage';
          break;
      case 'loggedOut':
          this.pageName = 'loginView';
          break;
      case 'courseSelected':
          this.courseSettingsService.fetchCourse();
          this.course = this.courseSettingsService.course
          this.pageName = 'tutoringView';
          break;
      case 'skillOverviewRequest':
        this.pageName = 'skillOverview'
        break;
      case 'closedProfile':
        this.initTask = sessionStorage.getItem("taskId")!;
        this.pageName = this.originPage;
        this.originPage = "";
        break;
      case 'profileRequest':
        this.originPage = this.pageName
        this.pageName = 'profileView';
        break;
      case 'homeRequest':
        this.pageName = 'welcomePage';
        this.initTask = null;
        break;
      case 'courseSettingsRequest':
        this.originPage = "tutoringView";
        this.pageName = 'courseSettings';
        break;
      case 'adminSettingsRequest':
          this.originPage = this.pageName;
          this.pageName = 'adminSettings';
          break;
      case 'settingsClosed':
        if (this.originPage == "tutoringView")
          {this.initTask = sessionStorage.getItem("taskId")!;}
        this.pageName = this.originPage;
        this.originPage = "";
        break;
      default:
        this.pageName = 'loginView'
          console.log("Invalid View request");
          break;
    }
  }
}
