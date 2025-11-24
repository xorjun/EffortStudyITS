import { Component } from '@angular/core';
import { EventEmitter } from '@angular/core';

@Component({
  selector: 'app-skill-overview',
  templateUrl: './skill-overview.component.html',
  styleUrls: ['./skill-overview.component.css']
})
export class SkillOverviewComponent {

  selectedCourse = "course1"
  courses = ["course1", "course2", "course3"]

  skills1 : any[] =[
    {
      name: "skill1",
      value : 50,
      progress : 25,
      explanation : "This is a nice LLM-generated explanation",
      associated_tasks: ["task1", "task2", "task5"]
    },
    {
      name: "skill2",
      value : 75,
      progress : 20,
      explanation : "This is a nice LLM-generated explanation",
      associated_tasks: ["task2", "task5"]
    },
    {
      name: "skill3",
      value : 30,
      progress : 10,
      explanation : "This is a nice LLM-generated explanation",
      associated_tasks: ["task1", "task5"]
    }
  ]

  skills = this.skills1

  skills2 : any[] =[
    {
      name: "skill1",
      value : 50,
      progress : 25,
      explanation : "This is a nice LLM-generated explanation",
      associated_tasks: ["task1", "task2", "task5"]
    },
    {
      name: "skill2",
      value : 75,
      progress : 20,
      explanation : "This is a nice LLM-generated explanation",
      associated_tasks: ["task2", "task5"]
    }
  ]

  onSelectedCourseChange(event: Event) {
    var newValue = "course2"
    this.selectedCourse = newValue;
    console.log(`Selected option: ${this.selectedCourse}`);

    if(newValue == "course2"){
      this.skills = this.skills2
    }
    else{
      this.skills = this.skills1
    }
  }
}
