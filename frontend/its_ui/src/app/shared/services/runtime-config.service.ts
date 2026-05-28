import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface AppwriteRuntimeConfig {
  endpoint: string;
  projectId: string;
  databaseId: string;
  downloadBucketId: string;
  adminTeamId: string;
  functions: {
    authInit: string;
    sessionStart: string;
    sessionComplete: string;
    generateSurveyUrl: string;
    aiProxy: string;
    checkBanners: string;
    submitBannerResponse: string;
    listBanners: string;
    saveBanner: string;
    deleteBanner: string;
    exportParticipants: string;
    exportBannerResponses: string;
    getStudyConfig: string;
    saveStudyConfig: string;
  };
}

interface RuntimeConfigPayload {
  appwrite?: Partial<AppwriteRuntimeConfig> & {
    functions?: Partial<AppwriteRuntimeConfig['functions']>;
  };
}

const EMPTY_RUNTIME_CONFIG: AppwriteRuntimeConfig = {
  endpoint: '',
  projectId: '',
  databaseId: '',
  downloadBucketId: '',
  adminTeamId: '',
  functions: {
    authInit: '',
    sessionStart: '',
    sessionComplete: '',
    generateSurveyUrl: '',
    aiProxy: '',
    checkBanners: '',
    submitBannerResponse: '',
    listBanners: '',
    saveBanner: '',
    deleteBanner: '',
    exportParticipants: '',
    exportBannerResponses: '',
    getStudyConfig: '',
    saveStudyConfig: '',
  },
};

@Injectable({
  providedIn: 'root'
})
export class RuntimeConfigService {
  private runtimeConfig: AppwriteRuntimeConfig = EMPTY_RUNTIME_CONFIG;

  constructor(private http: HttpClient) {}

  async load(): Promise<void> {
    try {
      const payload = await firstValueFrom(this.http.get<RuntimeConfigPayload>('assets/runtime-config.json', {
        headers: new HttpHeaders({
          'cache-control': 'no-cache',
        }),
      }));

      this.runtimeConfig = {
        ...EMPTY_RUNTIME_CONFIG,
        ...payload.appwrite,
        functions: {
          ...EMPTY_RUNTIME_CONFIG.functions,
          ...payload.appwrite?.functions,
        },
      };
    } catch (error) {
      console.warn('Failed to load runtime Appwrite config. Appwrite study features remain disabled.', error);
      this.runtimeConfig = EMPTY_RUNTIME_CONFIG;
    }
  }

  get appwrite(): AppwriteRuntimeConfig {
    return this.runtimeConfig;
  }
}
