import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface StudyContextState {
  initialized: boolean;
  participantId: string | null;
  participantUserId: string | null;
  condition: string | null;
  currentSession: number;
  jwt: string | null;
  sessionLogId: string | null;
}

const INITIAL_STATE: StudyContextState = {
  initialized: false,
  participantId: null,
  participantUserId: null,
  condition: null,
  currentSession: 1,
  jwt: null,
  sessionLogId: null,
};

@Injectable({
  providedIn: 'root'
})
export class StudyContextService {
  private readonly stateSubject = new BehaviorSubject<StudyContextState>(INITIAL_STATE);
  readonly state$ = this.stateSubject.asObservable();

  constructor() {
    const storedParticipantId = sessionStorage.getItem('studyParticipantId');
    const storedCondition = sessionStorage.getItem('studyCondition');
    const storedParticipantUserId = sessionStorage.getItem('studyParticipantUserId');
    const storedSessionLogId = sessionStorage.getItem('studySessionLogId');
    const storedCurrentSession = Number.parseInt(sessionStorage.getItem('studyCurrentSession') || '1', 10);

    if (storedParticipantId && storedCondition) {
      this.stateSubject.next({
        initialized: true,
        participantId: storedParticipantId,
        participantUserId: storedParticipantUserId,
        condition: storedCondition,
        currentSession: Number.isNaN(storedCurrentSession) ? 1 : storedCurrentSession,
        jwt: null,
        sessionLogId: storedSessionLogId,
      });
    }
  }

  get snapshot(): StudyContextState {
    return this.stateSubject.value;
  }

  update(patch: Partial<StudyContextState>): void {
    const nextState = { ...this.stateSubject.value, ...patch };
    this.stateSubject.next(nextState);

    if (nextState.participantId) {
      sessionStorage.setItem('studyParticipantId', nextState.participantId);
    }
    if (nextState.participantUserId) {
      sessionStorage.setItem('studyParticipantUserId', nextState.participantUserId);
    }
    if (nextState.condition) {
      sessionStorage.setItem('studyCondition', nextState.condition);
    }
    sessionStorage.setItem('studyCurrentSession', String(nextState.currentSession));
    if (nextState.sessionLogId) {
      sessionStorage.setItem('studySessionLogId', nextState.sessionLogId);
    }
  }
}
