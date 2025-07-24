import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { MarkdownModule, MarkedOptions } from 'ngx-markdown';
import { DatePipe } from '@angular/common';

import { CodePanelComponent } from './code-panel/code-panel.component';

import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { SharedModule } from './shared/shared.module';

import { HttpClientModule } from '@angular/common/http';

import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatOption, MatOptionModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';

import { TaskPanelComponent } from './task-panel/task-panel.component';
import { NavigationBarComponent } from './navigation-bar/navigation-bar.component';
import { FeedbackPanelComponent } from './feedback-panel/feedback-panel.component';
import { ActionPanelComponent } from './code-panel/action-panel/action-panel.component';
import { CodeEditorComponent } from './code-panel/code-editor/code-editor.component';
import { MultipleChoiceComponent } from './code-panel/multiple-choice/multiple-choice.component';
import { AuthComponent } from './auth/auth.component';
import { ProfileComponent } from './profile/profile.component';
import { CourseSelectionPanelComponent } from './course-selection-panel/course-selection-panel.component';
import { CourseSettingsComponent } from './course-settings/course-settings.component';
import { SettingsElementComponent } from './course-settings/settings-element/settings-element.component';
import { AdminSettingsComponent } from './admin-settings/admin-settings.component';
import { FeedbackSurveyComponent } from './feedback-panel/feedback-survey/feedback-survey.component';
import { StarRatingModule } from 'angular-star-rating';

@NgModule({
  declarations: [
    AppComponent,
    CodePanelComponent,
    TaskPanelComponent,
    NavigationBarComponent,
    FeedbackPanelComponent,
    ActionPanelComponent,
    CodeEditorComponent,
    MultipleChoiceComponent,
    AuthComponent,
    ProfileComponent,
    CourseSelectionPanelComponent,
    CourseSettingsComponent,
    SettingsElementComponent,
    AdminSettingsComponent,
    FeedbackSurveyComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    ReactiveFormsModule,
    SharedModule,
    MatButtonModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatOptionModule,
    StarRatingModule.forRoot(),
    MarkdownModule.forRoot({
      markedOptions: {
        provide: MarkedOptions,
        useValue: {
          gfm: false
        },
      },
    }),
  ],
  providers: [DatePipe],
  bootstrap: [AppComponent]
})
export class AppModule { }
