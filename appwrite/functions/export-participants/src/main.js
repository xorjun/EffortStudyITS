import { createAdminServices } from '../../shared/clients.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { toCsv } from '../../shared/csv.js';
import { handleFunctionError, textResponse } from '../../shared/http.js';
import { Query } from '../../shared/sdk.js';

export default async ({ req, res, error }) => {
  try {
    const { databases } = createAdminServices(req);
    const [participants, sessionLogs] = await Promise.all([
      databases.listDocuments({ databaseId: DATABASE_ID, collectionId: COLLECTIONS.PARTICIPANTS, queries: [Query.limit(500)] }),
      databases.listDocuments({ databaseId: DATABASE_ID, collectionId: COLLECTIONS.SESSION_LOGS, queries: [Query.limit(1000)] }),
    ]);

    const sessionsByParticipant = new Map();
    for (const sessionLog of sessionLogs.documents) {
      const participantLogs = sessionsByParticipant.get(sessionLog.participant_id) || new Map();
      participantLogs.set(sessionLog.session_number, sessionLog);
      sessionsByParticipant.set(sessionLog.participant_id, participantLogs);
    }

    const rows = [[
      'participant_id',
      'prolific_pid',
      'condition',
      'current_session',
      'pre_survey_completed',
      'day1_completed',
      'day2_completed',
      'study_completed',
      'session1_status',
      'session1_survey_completed',
      'session1_download_file_id',
      'session2_status',
      'session2_survey_completed',
      'session2_download_file_id',
      'enrolled_at',
    ]];

    for (const participant of participants.documents) {
      const participantSessions = sessionsByParticipant.get(participant.$id) || new Map();
      const session1 = participantSessions.get(1) || {};
      const session2 = participantSessions.get(2) || {};
      rows.push([
        participant.$id,
        participant.prolific_pid,
        participant.condition,
        participant.current_session,
        participant.pre_survey_completed,
        participant.day1_completed,
        participant.day2_completed,
        participant.study_completed,
        session1.completion_status || '',
        session1.survey_completed || false,
        session1.download_file_id || '',
        session2.completion_status || '',
        session2.survey_completed || false,
        session2.download_file_id || '',
        participant.enrolled_at,
      ]);
    }

    return textResponse(res, toCsv(rows), 200, {
      'content-type': 'text/csv; charset=utf-8',
      'content-disposition': 'attachment; filename="participants.csv"',
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
