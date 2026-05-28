import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';
import { AdminStudyBanner, StudyControlConfig, StudyFunctionsService } from '../shared/services/study-functions.service';

interface StudyMetricsSummary {
  participants: number;
  enrollments: number;
  tasks_attempted: number;
  tasks_completed: number;
  attempt_sessions: number;
  clipboard_events: number;
  paste_events: number;
  blocked_clipboard_events: number;
  state_snapshots: number;
  submissions: number;
  failed_submissions: number;
  runs: number;
  failed_runs: number;
  feedback_requests: number;
  total_logged_minutes: number;
  active_logged_minutes: number;
  idle_logged_minutes: number;
  max_code_complexity: number;
  ai_assisted_completed_tasks: number;
  ai_follow_up_actions: number;
  ai_exact_acceptance_rate: number;
  average_ai_modification_distance: number;
}

interface StudyMetricsRow {
  username: string;
  course_unique_name: string;
  current_course: string;
  roles: string[];
  data_collection_enabled: boolean;
  tasks_attempted: number;
  tasks_completed: number;
  attempt_sessions: number;
  clipboard_events: number;
  paste_events: number;
  blocked_clipboard_events: number;
  state_snapshots: number;
  submissions: number;
  failed_submissions: number;
  runs: number;
  failed_runs: number;
  feedback_requests: number;
  total_logged_minutes: number;
  active_logged_minutes: number;
  idle_logged_minutes: number;
  max_code_complexity: number;
  ai_assisted_completed_tasks: number;
  ai_follow_up_actions: number;
  ai_exact_acceptance_rate: number;
  average_ai_modification_distance: number;
  registered_utc?: string | null;
  last_activity_utc?: string | null;
}

interface StudyMetricsResponse {
  summary: StudyMetricsSummary;
  rows: StudyMetricsRow[];
}

@Component({
    selector: 'app-admin-settings',
    templateUrl: './admin-settings.component.html',
    styleUrls: ['./admin-settings.component.css'],
    imports: [CommonModule, ReactiveFormsModule]
})
export class AdminSettingsComponent {

  @Output() settingsClosedEvent: EventEmitter<string> = new EventEmitter<string>

  settingsForm!: FormGroup;
  metricsSummary: StudyMetricsSummary | null = null;
  metricsRows: StudyMetricsRow[] = [];
  metricsLoading: boolean = false;
  appwriteAdminReady: boolean = false;
  appwriteExportStatus: string = '';
  bannerCrudStatus: string = '';
  studyControlStatus: string = '';
  bannerLoading: boolean = false;
  banners: AdminStudyBanner[] = [];

  appwriteAdminForm!: FormGroup;
  bannerForm!: FormGroup;
  studyControlForm!: FormGroup;

  constructor(private client: HttpClient, public studyFunctionsService: StudyFunctionsService){
    this.settingsForm = new FormGroup({
      api_type: new FormControl(""),
      api_url: new FormControl(""),
      api_key: new FormControl(""),
      pedagogical_system_prompt: new FormControl(""),
      email_whitelist: new FormControl(""),
      disable_editor_copy_paste: new FormControl(false),
      live_preview_mode: new FormControl(false),
      final_preview_link_ttl_minutes: new FormControl(120),
    });

    this.appwriteAdminForm = new FormGroup({
      email: new FormControl(''),
      password: new FormControl(''),
      bannerId: new FormControl(''),
    });

    this.bannerForm = new FormGroup({
      id: new FormControl(''),
      name: new FormControl(''),
      message: new FormControl(''),
      triggerPosition: new FormControl('session-arrival'),
      inputsJson: new FormControl('[]'),
      triggerSessionFrom: new FormControl(1),
      triggerSessionTo: new FormControl(2),
      triggerAfterMinutes: new FormControl(0),
      isActive: new FormControl(false),
      isDismissable: new FormControl(true),
      blocksProgress: new FormControl(false),
      targetCondition: new FormControl('all'),
    });

    this.studyControlForm = new FormGroup({
      max_ai_queries_per_session: new FormControl(20),
      max_ai_queries_per_day: new FormControl(60),
      ai_query_cooldown_seconds: new FormControl(20),
      ai_max_prompt_chars: new FormControl(4000),
      ai_max_code_chars: new FormControl(12000),
      final_preview_link_ttl_minutes: new FormControl(120),
    });
  }

  ngOnInit() {
    this.loadSettings();
    this.loadMetrics();
  }

  loadSettings() {
    this.client.get<any>(`${environment.apiUrl}/settings/get`, {"withCredentials": true}).subscribe(
      (data) => {
        this.settingsForm.patchValue({
          api_type: data.api_type,
          api_url: data.api_url,
          api_key: data.api_key,
          pedagogical_system_prompt: data.pedagogical_system_prompt || "",
          email_whitelist: data.email_whitelist.join(","),
          disable_editor_copy_paste: !!data.disable_editor_copy_paste,
          live_preview_mode: !!data.live_preview_mode,
          final_preview_link_ttl_minutes: Number(data.final_preview_link_ttl_minutes || 120),
        });
        sessionStorage.setItem('livePreviewMode', String(!!data.live_preview_mode));
      }
    );
  }

  loadMetrics(): void {
    this.metricsLoading = true;
    this.client.get<StudyMetricsResponse>(`${environment.apiUrl}/settings/study_metrics`, {"withCredentials": true}).subscribe({
      next: (data) => {
        this.metricsSummary = data.summary;
        this.metricsRows = data.rows;
        this.metricsLoading = false;
      },
      error: () => {
        this.metricsSummary = null;
        this.metricsRows = [];
        this.metricsLoading = false;
      }
    });
  }

  saveStatus: string = '';
  private saveStatusTimer: any = null;

  saveSettings(): void {
    var settings: any = this.settingsForm.value;
    settings["email_whitelist"] = settings["email_whitelist"]
      .split(",")
      .map((entry: string) => entry.trim())
      .filter((entry: string) => entry.length > 0);
    settings["disable_editor_copy_paste"] = !!settings["disable_editor_copy_paste"];
    settings["live_preview_mode"] = !!settings["live_preview_mode"];
    settings["final_preview_link_ttl_minutes"] = Number(settings["final_preview_link_ttl_minutes"] || 120);
    sessionStorage.setItem('livePreviewMode', String(settings["live_preview_mode"]));
    this.client.post<any>(`${environment.apiUrl}/settings/update`, settings, {"withCredentials": true}).subscribe({
      next: () => this.showSaveStatus('Settings saved.'),
      error: () => this.showSaveStatus('Save failed — check your connection.'),
    });
  }

  private showSaveStatus(message: string): void {
    this.saveStatus = message;
    if (this.saveStatusTimer) { clearTimeout(this.saveStatusTimer); }
    this.saveStatusTimer = setTimeout(() => { this.saveStatus = ''; }, 4000);
  }

  closeSettings(): void {
    this.settingsClosedEvent.emit("settingsClosed")
  }

  async loginAppwriteAdmin(): Promise<void> {
    try {
      await this.studyFunctionsService.createAdminSession(
        this.appwriteAdminForm.value.email,
        this.appwriteAdminForm.value.password,
      );
      this.appwriteAdminReady = true;
      this.appwriteExportStatus = 'Appwrite admin session active.';
      await this.loadBanners();
      await this.loadStudyControls();
    } catch {
      this.appwriteAdminReady = false;
      this.appwriteExportStatus = 'Appwrite admin login failed.';
    }
  }

  async loadStudyControls(): Promise<void> {
    if (!this.appwriteAdminReady) {
      return;
    }
    try {
      const config = await this.studyFunctionsService.getStudyControlConfig();
      this.studyControlForm.patchValue(config);
      this.studyControlStatus = 'Loaded AI abuse controls.';
    } catch {
      this.studyControlStatus = 'Loading AI abuse controls failed.';
    }
  }

  async saveStudyControls(): Promise<void> {
    if (!this.appwriteAdminReady) {
      this.studyControlStatus = 'Connect an Appwrite admin session before saving controls.';
      return;
    }

    const payload: StudyControlConfig = {
      max_ai_queries_per_session: Number(this.studyControlForm.value.max_ai_queries_per_session || 20),
      max_ai_queries_per_day: Number(this.studyControlForm.value.max_ai_queries_per_day || 60),
      ai_query_cooldown_seconds: Number(this.studyControlForm.value.ai_query_cooldown_seconds || 20),
      ai_max_prompt_chars: Number(this.studyControlForm.value.ai_max_prompt_chars || 4000),
      ai_max_code_chars: Number(this.studyControlForm.value.ai_max_code_chars || 12000),
      final_preview_link_ttl_minutes: Number(this.studyControlForm.value.final_preview_link_ttl_minutes || 120),
    };

    try {
      const saved = await this.studyFunctionsService.saveStudyControlConfig(payload);
      this.studyControlForm.patchValue(saved);
      this.studyControlStatus = 'Saved AI abuse controls.';
    } catch {
      this.studyControlStatus = 'Saving AI abuse controls failed.';
    }
  }

  async loadBanners(): Promise<void> {
    if (!this.appwriteAdminReady) {
      return;
    }

    this.bannerLoading = true;
    try {
      this.banners = await this.studyFunctionsService.listBanners();
      this.bannerCrudStatus = this.banners.length > 0 ? 'Loaded Appwrite banners.' : 'No Appwrite banners created yet.';
    } catch {
      this.bannerCrudStatus = 'Loading Appwrite banners failed.';
    } finally {
      this.bannerLoading = false;
    }
  }

  editBanner(banner: AdminStudyBanner): void {
    this.bannerForm.patchValue({
      id: banner.id,
      name: banner.name,
      message: banner.message,
      triggerPosition: banner.triggerPosition,
      inputsJson: JSON.stringify(banner.inputs, null, 2),
      triggerSessionFrom: banner.triggerSessionFrom,
      triggerSessionTo: banner.triggerSessionTo,
      triggerAfterMinutes: banner.triggerAfterMinutes,
      isActive: banner.isActive,
      isDismissable: banner.isDismissable,
      blocksProgress: banner.blocksProgress,
      targetCondition: banner.targetCondition,
    });
    this.appwriteAdminForm.patchValue({ bannerId: banner.id });
    this.bannerCrudStatus = `Editing banner ${banner.name}.`;
  }

  resetBannerForm(): void {
    this.bannerForm.reset({
      id: '',
      name: '',
      message: '',
      triggerPosition: 'session-arrival',
      inputsJson: '[]',
      triggerSessionFrom: 1,
      triggerSessionTo: 2,
      triggerAfterMinutes: 0,
      isActive: false,
      isDismissable: true,
      blocksProgress: false,
      targetCondition: 'all',
    });
  }

  async saveBanner(): Promise<void> {
    if (!this.appwriteAdminReady) {
      this.bannerCrudStatus = 'Connect an Appwrite admin session before saving banners.';
      return;
    }

    try {
      await this.studyFunctionsService.saveBanner({
        id: this.bannerForm.value.id,
        name: this.bannerForm.value.name,
        message: this.bannerForm.value.message,
        triggerPosition: this.bannerForm.value.triggerPosition,
        inputsJson: this.bannerForm.value.inputsJson,
        triggerSessionFrom: Number(this.bannerForm.value.triggerSessionFrom),
        triggerSessionTo: Number(this.bannerForm.value.triggerSessionTo),
        triggerAfterMinutes: Number(this.bannerForm.value.triggerAfterMinutes),
        isActive: !!this.bannerForm.value.isActive,
        isDismissable: !!this.bannerForm.value.isDismissable,
        blocksProgress: !!this.bannerForm.value.blocksProgress,
        targetCondition: this.bannerForm.value.targetCondition,
      });
      this.bannerCrudStatus = 'Banner saved.';
      this.resetBannerForm();
      await this.loadBanners();
    } catch {
      this.bannerCrudStatus = 'Saving banner failed. Check the JSON and session values.';
    }
  }

  async deleteBanner(bannerId: string): Promise<void> {
    if (!this.appwriteAdminReady) {
      return;
    }

    try {
      await this.studyFunctionsService.deleteBanner(bannerId);
      if (this.bannerForm.value.id === bannerId) {
        this.resetBannerForm();
      }
      if (this.appwriteAdminForm.value.bannerId === bannerId) {
        this.appwriteAdminForm.patchValue({ bannerId: '' });
      }
      this.bannerCrudStatus = 'Banner deleted.';
      await this.loadBanners();
    } catch {
      this.bannerCrudStatus = 'Deleting banner failed.';
    }
  }

  async exportParticipants(): Promise<void> {
    try {
      const csv = await this.studyFunctionsService.exportParticipantsCsv();
      this.downloadCsv(csv, 'participants.csv');
      this.appwriteExportStatus = 'Participant export downloaded.';
    } catch {
      this.appwriteExportStatus = 'Participant export failed.';
    }
  }

  async exportBannerResponses(): Promise<void> {
    const bannerId = this.appwriteAdminForm.value.bannerId;
    if (!bannerId) {
      this.appwriteExportStatus = 'Banner ID is required for banner response export.';
      return;
    }

    try {
      const csv = await this.studyFunctionsService.exportBannerResponsesCsv(bannerId);
      this.downloadCsv(csv, `banner-${bannerId}.csv`);
      this.appwriteExportStatus = 'Banner export downloaded.';
    } catch {
      this.appwriteExportStatus = 'Banner export failed.';
    }
  }

  private downloadCsv(csv: string, filename: string): void {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  trackBanner(_index: number, banner: AdminStudyBanner): string {
    return banner.id;
  }

}
