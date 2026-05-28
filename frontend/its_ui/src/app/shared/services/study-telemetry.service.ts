import { Injectable } from '@angular/core';
import { ID, Permission, Role } from 'appwrite';
import { AppwriteClientService } from './appwrite-client.service';
import { StudyContextService } from './study-context.service';
import { RuntimeConfigService } from './runtime-config.service';

interface TelemetryQueueItem {
  eventType: string;
  sessionNumber: number;
  payload: unknown;
  clientTs: string;
}

interface StudyEventContext {
  courseId: string | null;
  taskId: string | null;
  taskType: string | null;
  currentTopic: string | null;
  feedbackAvailable: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class StudyTelemetryService {
  private readonly queue: TelemetryQueueItem[] = [];
  private flushInFlight = false;

  constructor(
    private appwrite: AppwriteClientService,
    private studyContext: StudyContextService,
    private runtimeConfigService: RuntimeConfigService,
  ) {
    window.setInterval(() => {
      void this.flush();
    }, 10000);
  }

  logEvent(eventType: string, payload: unknown, sessionNumber?: number): void {
    const state = this.studyContext.snapshot;
    if (!this.appwrite.isConfigured || !state.initialized || !state.participantId || !state.participantUserId) {
      return;
    }

    this.queue.push({
      eventType,
      sessionNumber: sessionNumber || state.currentSession,
      payload,
      clientTs: new Date().toISOString(),
    });
  }

  logContextEvent(eventType: string, payload: Record<string, unknown> = {}, sessionNumber?: number): void {
    this.logEvent(eventType, {
      ...payload,
      context: this.getStudyContext(),
    }, sessionNumber);
  }

  private getStudyContext(): StudyEventContext {
    return {
      courseId: sessionStorage.getItem('courseID'),
      taskId: sessionStorage.getItem('taskId'),
      taskType: sessionStorage.getItem('taskType'),
      currentTopic: sessionStorage.getItem('currentTopic'),
      feedbackAvailable: sessionStorage.getItem('feedbackAvailable'),
    };
  }

  private async flush(): Promise<void> {
    const state = this.studyContext.snapshot;
    if (this.flushInFlight || this.queue.length === 0 || !state.participantId || !state.participantUserId) {
      return;
    }

    this.flushInFlight = true;
    const batch = this.queue.splice(0, this.queue.length);

    try {
      const config = this.runtimeConfigService.appwrite;
      for (const item of batch) {
        await this.appwrite.databases.createDocument(
          config.databaseId,
          'telemetry_events',
          ID.unique(),
          {
            participant_id: state.participantId,
            event_type: item.eventType.slice(0, 32),
            session_number: item.sessionNumber,
            payload: JSON.stringify(item.payload).slice(0, 5000),
            client_ts: item.clientTs,
            server_ts: new Date().toISOString(),
          },
          [
            Permission.read(Role.user(state.participantUserId)),
            Permission.write(Role.team(config.adminTeamId)),
          ],
        );
      }
    } catch {
      this.queue.unshift(...batch);
    } finally {
      this.flushInFlight = false;
    }
  }
}
