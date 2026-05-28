import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { buildSessionArchive } from '../../shared/archive.js';
import { DOWNLOAD_BUCKET_ID } from '../../shared/constants.js';
import { buildSurveyUrl } from '../../shared/survey.js';
import { getParticipantByUserId } from '../../shared/participants.js';
import { getSessionLog, upsertSessionLog } from '../../shared/sessions.js';
import { handleFunctionError, HttpError, jsonResponse, parseInteger, parseOptionalInteger, readJsonBody, requireMethod } from '../../shared/http.js';
import { InputFile } from '../../shared/sdk.js';
import { participantReadOnlyFilePermissions } from '../../shared/permissions.js';

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const { userId } = requireAuthenticatedUser(req);
    const body = readJsonBody(req);
    const sessionNumber = parseInteger(body.session_number || body.sessionNumber, 'session_number');
    const code = String(body.code || body.submitted_code || '');
    const completionStatus = String(body.completion_status || body.completionStatus || 'completed');
    const testsPassed = parseOptionalInteger(body.tests_passed || body.testsPassed, 0);
    const testsTotal = parseOptionalInteger(body.tests_total || body.testsTotal, 0);

    const { databases, storage } = createAdminServices(req);
    const participant = await getParticipantByUserId(databases, userId);
    if (!participant) {
      throw new HttpError(404, 'No participant is bound to the current user.');
    }

    const existingLog = await getSessionLog(databases, participant.$id, sessionNumber);
    const sessionLog = await upsertSessionLog(databases, userId, participant.$id, sessionNumber, {
      started_at: existingLog?.started_at || new Date().toISOString(),
      completed_at: new Date().toISOString(),
      completion_status: completionStatus,
      final_code: code,
      download_triggered: true,
      tests_passed: testsPassed,
      tests_total: testsTotal,
    });

    const zipBuffer = await buildSessionArchive({
      participantId: participant.$id,
      sessionNumber,
      completionStatus,
      code,
      testsPassed,
      testsTotal,
    });

    const filename = `participant-${participant.$id.slice(0, 8)}-session-${sessionNumber}.zip`;
    const uploadedFile = await storage.createFile({
      bucketId: DOWNLOAD_BUCKET_ID,
      fileId: 'unique()',
      file: InputFile.fromBuffer(zipBuffer, filename),
      permissions: participantReadOnlyFilePermissions(userId),
    });

    await upsertSessionLog(databases, userId, participant.$id, sessionNumber, {
      started_at: sessionLog.started_at,
      completed_at: sessionLog.completed_at,
      completion_status: completionStatus,
      final_code: code,
      download_triggered: true,
      download_file_id: uploadedFile.$id,
      tests_passed: testsPassed,
      tests_total: testsTotal,
    });

    return jsonResponse(res, {
      fileId: uploadedFile.$id,
      surveyUrl: buildSurveyUrl({
        pid: participant.prolific_pid,
        condition: participant.condition,
        sessionNumber,
        phase: 'post',
      }),
      sessionLogId: sessionLog.$id,
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
