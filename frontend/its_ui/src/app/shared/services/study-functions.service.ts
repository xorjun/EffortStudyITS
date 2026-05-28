import { Injectable } from '@angular/core';
import { ExecutionMethod } from 'appwrite';
import { AppwriteClientService } from './appwrite-client.service';
import { StudyContextService } from './study-context.service';
import { AppwriteRuntimeConfig, RuntimeConfigService } from './runtime-config.service';

interface FunctionExecutionResponse<T> {
  responseBody: string;
  responseStatusCode: number;
}

interface AuthInitResponse {
  participantId: string;
  participantUserId: string;
  condition: string;
  currentSession: number;
  token: string;
}

interface SessionStartResponse {
  sessionLogId: string;
  sessionNumber: number;
}

interface AiProxyResponse {
  responseText: string;
  tokensUsed: number;
  remainingQueries: number;
  remainingDailyQueries?: number;
}

export interface StudyControlConfig {
  max_ai_queries_per_session: number;
  max_ai_queries_per_day: number;
  ai_query_cooldown_seconds: number;
  ai_max_prompt_chars: number;
  ai_max_code_chars: number;
  final_preview_link_ttl_minutes: number;
}

export interface StudyBanner {
  id: string;
  name: string;
  message: string;
  triggerPosition: string;
  blocksProgress: boolean;
  isDismissable: boolean;
  shownAt: string;
  inputs: Array<Record<string, unknown> | string>;
}

export interface AdminStudyBanner extends StudyBanner {
  triggerSessionFrom: number;
  triggerSessionTo: number;
  triggerAfterMinutes: number;
  isActive: boolean;
  createdAt?: string;
  updatedAt?: string;
  targetCondition: string;
}

interface CheckBannersResponse {
  banners: StudyBanner[];
}

interface SessionCompleteResponse {
  fileId: string;
  surveyUrl: string;
  sessionLogId: string;
  previewUrl?: string;
}

interface ListBannersResponse {
  banners: AdminStudyBanner[];
}

interface SaveBannerResponse {
  banner: AdminStudyBanner;
}

interface StudyConfigResponse extends StudyControlConfig {}

@Injectable({
  providedIn: 'root'
})
export class StudyFunctionsService {
  private initializePromise: Promise<AuthInitResponse | null> | null = null;
  private autosaveTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private appwrite: AppwriteClientService,
    private studyContext: StudyContextService,
    private runtimeConfigService: RuntimeConfigService,
  ) {}

  private get config(): AppwriteRuntimeConfig {
    return this.runtimeConfigService.appwrite;
  }

  get isConfigured(): boolean {
    return this.appwrite.isConfigured;
  }

  canUseAiAssistance(): boolean {
    const state = this.studyContext.snapshot;
    return this.isConfigured && state.initialized && state.condition === 'A';
  }

  async initializeFromUrl(): Promise<AuthInitResponse | null> {
    if (!this.isConfigured) {
      return null;
    }
    if (this.initializePromise) {
      return this.initializePromise;
    }

    const params = new URLSearchParams(window.location.search);
    const prolificPid = params.get('PROLIFIC_PID');
    if (!prolificPid) {
      return null;
    }

    this.initializePromise = (async () => {
      await this.appwrite.ensureAnonymousSession();

      const authResponse = await this.executeJson<AuthInitResponse>(this.config.functions.authInit, {
        PROLIFIC_PID: prolificPid,
        STUDY_ID: params.get('STUDY_ID'),
        SESSION_ID: params.get('SESSION_ID'),
        prior_exp: params.get('prior_exp'),
      });

      this.studyContext.update({
        initialized: true,
        participantId: authResponse.participantId,
        participantUserId: authResponse.participantUserId,
        condition: authResponse.condition,
        currentSession: authResponse.currentSession,
        jwt: null,
      });

      await this.ensureActiveSession(authResponse.currentSession);
      return authResponse;
    })();

    return this.initializePromise;
  }

  async ensureActiveSession(sessionNumber?: number): Promise<SessionStartResponse | null> {
    const state = this.studyContext.snapshot;
    if (!this.isConfigured || !state.initialized) {
      return null;
    }

    const response = await this.executeJson<SessionStartResponse>(this.config.functions.sessionStart, {
      session_number: sessionNumber || state.currentSession,
    });

    this.studyContext.update({
      currentSession: response.sessionNumber,
      sessionLogId: response.sessionLogId,
    });
    return response;
  }

  scheduleAutosave(code: string): void {
    const state = this.studyContext.snapshot;
    if (!this.isConfigured || !state.sessionLogId) {
      return;
    }

    if (this.autosaveTimer) {
      clearTimeout(this.autosaveTimer);
    }

    this.autosaveTimer = setTimeout(() => {
      void this.appwrite.databases.updateDocument(
        this.config.databaseId,
        'session_logs',
        state.sessionLogId!,
        {
          final_code: code.slice(0, 50000),
        },
      ).catch(() => undefined);
    }, 30000);
  }

  async requestAiHint(prompt: string, currentCode: string): Promise<AiProxyResponse> {
    const state = this.studyContext.snapshot;
    return this.executeJson<AiProxyResponse>(this.config.functions.aiProxy, {
      session_number: state.currentSession,
      messages: [{ role: 'user', content: prompt }],
      current_code: currentCode,
    });
  }

  async checkBanners(firedEvents: string[], elapsedMinutes: number): Promise<StudyBanner[]> {
    const state = this.studyContext.snapshot;
    const response = await this.executeJson<CheckBannersResponse>(this.config.functions.checkBanners, {
      session_number: state.currentSession,
      fired_events: firedEvents,
      elapsed_minutes: elapsedMinutes,
    });

    return response.banners;
  }

  async submitBannerResponse(bannerId: string, shownAt: string, responseData: Record<string, unknown>, wasDismissed = false): Promise<void> {
    const state = this.studyContext.snapshot;
    await this.executeJson(this.config.functions.submitBannerResponse, {
      banner_id: bannerId,
      shown_at: shownAt,
      session_number: state.currentSession,
      response_data: responseData,
      was_dismissed: wasDismissed,
      trigger_event: 'ui-overlay',
    });
  }

  async createAdminSession(email: string, password: string): Promise<void> {
    await this.appwrite.createEmailSession(email, password);
  }

  async listBanners(): Promise<AdminStudyBanner[]> {
    const response = await this.executeJson<ListBannersResponse>(this.config.functions.listBanners, {});
    return response.banners;
  }

  async saveBanner(banner: {
    id?: string | null;
    name: string;
    message: string;
    triggerPosition: string;
    inputsJson: string;
    triggerSessionFrom: number;
    triggerSessionTo: number;
    triggerAfterMinutes: number;
    isActive: boolean;
    isDismissable: boolean;
    blocksProgress: boolean;
    targetCondition: string;
  }): Promise<AdminStudyBanner> {
    const response = await this.executeJson<SaveBannerResponse>(this.config.functions.saveBanner, {
      banner_id: banner.id,
      name: banner.name,
      message: banner.message,
      trigger_position: banner.triggerPosition,
      inputs_json: banner.inputsJson,
      trigger_session_from: banner.triggerSessionFrom,
      trigger_session_to: banner.triggerSessionTo,
      trigger_after_minutes: banner.triggerAfterMinutes,
      is_active: banner.isActive,
      is_dismissable: banner.isDismissable,
      blocks_progress: banner.blocksProgress,
      target_condition: banner.targetCondition,
    });
    return response.banner;
  }

  async deleteBanner(bannerId: string): Promise<void> {
    await this.executeJson(this.config.functions.deleteBanner, {
      banner_id: bannerId,
    });
  }

  async exportParticipantsCsv(): Promise<string> {
    return this.executeText(this.config.functions.exportParticipants);
  }

  async exportBannerResponsesCsv(bannerId: string): Promise<string> {
    return this.executeText(this.config.functions.exportBannerResponses, {
      banner_id: bannerId,
    });
  }

  async getStudyControlConfig(): Promise<StudyControlConfig> {
    return this.executeJson<StudyConfigResponse>(this.config.functions.getStudyConfig, {});
  }

  async saveStudyControlConfig(config: StudyControlConfig): Promise<StudyControlConfig> {
    return this.executeJson<StudyConfigResponse>(this.config.functions.saveStudyConfig, config);
  }

  async completeCurrentSession(code: string, testsPassed = 0, testsTotal = 0): Promise<SessionCompleteResponse> {
    const state = this.studyContext.snapshot;
    const response = await this.executeJson<SessionCompleteResponse>(this.config.functions.sessionComplete, {
      session_number: state.currentSession,
      code,
      completion_status: 'completed',
      tests_passed: testsPassed,
      tests_total: testsTotal,
    });

    this.studyContext.update({
      sessionLogId: response.sessionLogId,
    });

    return response;
  }

  getDownloadUrl(fileId: string): string {
    return this.appwrite.storage.getFileDownload(this.config.downloadBucketId, fileId).toString();
  }

  private async executeJson<T>(functionId: string, body: unknown): Promise<T> {
    const execution = await this.createExecution(functionId, body);
    const payload = execution.responseBody ? JSON.parse(execution.responseBody) : {};
    if (execution.responseStatusCode >= 400) {
      throw new Error(payload.error || `Function ${functionId} failed.`);
    }
    return payload as T;
  }

  private async executeText(functionId: string, body?: unknown): Promise<string> {
    const execution = await this.createExecution(functionId, body);
    if (execution.responseStatusCode >= 400) {
      throw new Error(execution.responseBody || `Function ${functionId} failed.`);
    }
    return execution.responseBody || '';
  }

  private async createExecution(functionId: string, body?: unknown): Promise<FunctionExecutionResponse<unknown>> {
    return await this.appwrite.functions.createExecution(
      functionId,
      body ? JSON.stringify(body) : undefined,
      false,
      '/',
      ExecutionMethod.POST,
      {
        'content-type': 'application/json',
      },
    ) as unknown as FunctionExecutionResponse<unknown>;
  }
}
