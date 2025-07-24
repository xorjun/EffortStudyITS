import { Component, Input, Output, OnInit } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'app-settings-element',
  templateUrl: './settings-element.component.html',
  styleUrls: ['./settings-element.component.css']
})
export class SettingsElementComponent {

  @Input('setting') setting!: string
  @Input() form!: FormGroup
  @Input() setting_data: any

  settingName!: string
  settingInput!: string

  constructor(){
    
  }

  ngOnInit(){
    this.renderSetting();
  }

  renderSetting(){
    switch ( this.setting ) {
      case "feedback_init_time":
          this.settingName = "Initialization Time";
          break;
      case "feedback_cooldown":
          this.settingName = "Feedback Cooldown";
          break;
      case "sample_settings":
        this.settingName = "A/B test Probabilities";
        break;
      case "pedagogical_model":
          this.settingName = "Pedagogical Model";
          break;
      case "language_generation_model":
          this.settingName = "Language generation Model";
          break;
      default: 
          // 
          break;
   }
  }

}
