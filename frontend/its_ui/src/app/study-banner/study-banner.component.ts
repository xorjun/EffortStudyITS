import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormArray, FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { StudyBannerService } from '../shared/services/study-banner.service';
import { StudyBanner } from '../shared/services/study-functions.service';

@Component({
  selector: 'app-study-banner',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './study-banner.component.html',
  styleUrls: ['./study-banner.component.css']
})
export class StudyBannerComponent {
  readonly banner$ = this.studyBannerService.currentBanner$;
  readonly form = new FormGroup({
    responses: new FormArray<FormControl<string>>([]),
  });

  constructor(private studyBannerService: StudyBannerService) {
    this.banner$.subscribe((banner) => {
      this.prepareForm(banner);
    });
  }

  get responses(): FormArray<FormControl<string>> {
    return this.form.controls.responses;
  }

  prepareForm(banner: StudyBanner | null): void {
    this.responses.clear();
    if (!banner) {
      return;
    }

    banner.inputs.forEach(() => {
      this.responses.push(new FormControl('', { nonNullable: true }));
    });
  }

  getOptions(input: Record<string, unknown> | string): string[] {
    if (typeof input === 'string') {
      return [];
    }

    const options = input['options'] || input['choices'];
    if (!Array.isArray(options)) {
      return [];
    }

    return options.map((option) => typeof option === 'string' ? option : String((option as Record<string, unknown>)['label'] || (option as Record<string, unknown>)['value'] || ''));
  }

  getLabel(input: Record<string, unknown> | string, index: number): string {
    if (typeof input === 'string') {
      return input;
    }

    return String(input['label'] || input['name'] || `Response ${index + 1}`);
  }

  isLongText(input: Record<string, unknown> | string): boolean {
    return typeof input !== 'string' && String(input['type'] || '').toLowerCase() === 'textarea';
  }

  async submit(): Promise<void> {
    const responseData = Object.fromEntries(this.responses.controls.map((control, index) => [String(index), control.value]));
    await this.studyBannerService.submitCurrentResponse(responseData, false);
    this.prepareForm(null);
  }

  async dismiss(): Promise<void> {
    await this.studyBannerService.submitCurrentResponse({}, true);
    this.prepareForm(null);
  }
}
