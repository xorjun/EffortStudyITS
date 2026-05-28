import { Component, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { MarkdownPanelComponent } from '../shared/components/markdown-panel/markdown-panel.component';

export interface CourseDescription{
  unique_name: string;
  display_name: string;
}

@Component({
    selector: 'app-skill-overview',
    templateUrl: './skill-overview.component.html',
    styleUrls: ['./skill-overview.component.css'],
    imports: [CommonModule, MarkdownPanelComponent]
})
export class SkillOverviewComponent {

  @ViewChild('reasonPopup', {static: true}) reasonPopup!: ElementRef<HTMLDialogElement>;
  @ViewChild('explanationPopup', {static: true}) explanationPopup!: ElementRef<HTMLDialogElement>;

  reasonMarkdown: string = '';
  explanationMarkdown: string = '';

  courses : CourseDescription[]= [];
  selectedCourse : string | null = null;

  course_value  = 59;
  course_progress = 15; 

  skills : any[] = []
  
  constructor(
      private client: HttpClient,
    ){
    }

  ngOnInit(): void {
    this.fetchCourseInfo()
  }

  //TODO: only do this for courses the user is enrolled in (needs additional request)
  fetchCourseInfo(){
    const endpoint_url = `${environment.apiUrl}/course/info/`;
    this.client.get<any>(endpoint_url, {withCredentials: true}).subscribe((data) => { 
      this.courses =  data.course_list;
      if (this.courses.length > 0)
      {
        this.selectedCourse = this.courses[0].unique_name
        this.loadSkillsForCourse(this.courses[0].unique_name)
      }
  });
  }

  onSelectedCourseChange() {
    var e : any = document.getElementById("skill-overview-course-selection")
    var newValue = e.value
    this.selectedCourse = newValue
    console.log(`Selected option: ${this.selectedCourse}`);

    this.loadSkillsForCourse(newValue)
  }

  loadSkillsForCourse(courseUniqueName: string){
    const endpoint_url = `${environment.apiUrl}/skills/${courseUniqueName}/`;
    this.client.get<any>(endpoint_url, {withCredentials: true}).subscribe((data) => {
      this.skills = data.skill_list
    })
  }
  

  generateExplanation(skillName: string){
    const endpoint_url = `${environment.apiUrl}/skills/${this.selectedCourse}/${skillName}/explanation`;
    this.client.get<any>(endpoint_url, {withCredentials: true}).subscribe((data) => {
      this.explanationMarkdown = data.explanation
      this.explanationPopup.nativeElement.showModal();
    })
    // TODO: maybe some sort of indicator to wait
  }

  generateReason(skillName: string){
    const endpoint_url = `${environment.apiUrl}/skills/${this.selectedCourse}/${skillName}/reason`;
    this.client.get<any>(endpoint_url, {withCredentials: true}).subscribe((data) => {
      this.reasonMarkdown = data.reason
    })
    this.reasonPopup.nativeElement.showModal();
  }

  
  suggestNextSteps()
  {
    //TODO; implement method
  }
}
