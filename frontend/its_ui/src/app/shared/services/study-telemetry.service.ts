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

const MAX_QUEUE_SIZE = 500;
const FLUSH_INTERVAL_MS = 10_000;

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
    }, FLUSH_INTERVAL_MS);

    // Flush on tab close / navigation — sendBeacon is fire-and-forget and works
    // even after the page starts unloading.
    window.addEventListener('beforeunload', () => {
      this.flushSync();
    });
  }

  logEvent(eventType: string, payload: unknown, sessionNumber?: number): void {
    const state = this.studyContext.snapshot;
    if (!this.appwrite.isConfigured || !state.initialized || !state.participantId || !state.participantUserId) {
      return;
    }

    // Cap the queue — evict oldest events first to prevent memory leaks during
    // prolonged Appwrite outages.
    if (this.queue.length >= MAX_QUEUE_SIZE) {
      this.queue.shift();
      console.warn(
        `[StudyTelemetry] Queue exceeded ${MAX_QUEUE_SIZE} items — oldest event discarded. ` +
        'Check Appwrite connectivity.',
      );
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

  /** Synchronous flush via sendBeacon — used on page unload. */
  private flushSync(): void {
    if (this.queue.length === 0) return;
    const state = this.studyContext.snapshot;
    if (!state.participantId || !state.participantUserId) return;
    const batch = this.queue.splice(0, this.queue.length);
    const payload = JSON.stringify({
      participant_id: state.participantId,
      participant_user_id: state.participantUserId,
      events: batch.map(item => ({
        event_type: item.eventType.slice(0, 32),
        session_number: item.sessionNumber,
        payload: JSON.stringify(item.payload).slice(0, 5000),
        client_ts: item.clientTs,
      })),
    });
    // Fire-and-forget — sendBeacon is the only reliable way to send data
    // during page unload.
    const config = this.runtimeConfigService.appwrite;
    const url = `${config.endpoint}/databases/${config.databaseId}/collections/telemetry_events/documents`;
    navigator.sendBeacon(url, new Blob([payload], { type: 'application/json' }));
  }

  /** Async flush — writes events in parallel, re-queues only failures. */
  private async flush(): Promise<void> {
    const state = this.studyContext.snapshot;
    if (this.flushInFlight || this.queue.length === 0 || !state.participantId || !state.participantUserId) {
      return;
    }

    this.flushInFlight = true;
    const batch = this.queue.splice(0, this.queue.length);
    const config = this.runtimeConfigService.appwrite;
    const failed: TelemetryQueueItem[] = [];

    // Write all events in parallel — avoids N sequential round-trips.
    const results = await Promise.allSettled(
      batch.map(item =>
        this.appwrite.databases.createDocument(
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
            Permission.read(Role.user(state.participantUserId!)),
            Permission.write(Role.team(config.adminTeamId)),
          ],
        ),
      ),
    );

    for (let i = 0; i < results.length; i++) {
      if (results[i].status === 'rejected') {
        failed.push(batch[i]);
      }
    }

    // Re-queue only failed items — not the entire batch.
    if (failed.length > 0) {
      console.warn(`[StudyTelemetry] ${failed.length}/${batch.length} events failed — re-queuing.`);
      this.queue.unshift(...failed);
    }

    this.flushInFlight = false;
  }
}
