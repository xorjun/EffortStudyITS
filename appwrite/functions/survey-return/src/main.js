import { createAdminServices } from '../../shared/clients.js';
import { buildReturnUrl, verifySurveyToken } from '../../shared/survey.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { getParticipantByPid } from '../../shared/participants.js';
import { getSessionLog } from '../../shared/sessions.js';
import { HttpError, handleFunctionError, redirectResponse, requireMethod, textResponse } from '../../shared/http.js';

function prolificCompletionUrl(code) {
  return `https://app.prolific.com/submissions/complete?cc=${encodeURIComponent(code)}`;
}

function expiredHtml() {
  return `<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Survey Link Expired</title></head>
  <body style="font-family: sans-serif; padding: 2rem; max-width: 40rem; margin: 0 auto;">
    <h1>Survey Link Expired</h1>
    <p>This link is no longer valid. Please return to the study portal and request a fresh survey redirect.</p>
    <a href="${buildReturnUrl(1)}" style="display: inline-block; margin-top: 1rem; padding: 0.75rem 1rem; background: #0f766e; color: white; text-decoration: none; border-radius: 0.5rem;">Return to study portal</a>
  </body>
</html>`;
}

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'GET');
    const pid = req.query.pid;
    const phase = req.query.phase;
    const sessionNumber = Number.parseInt(String(req.query.session || '1'), 10);
    const sosciCase = req.query.sosci_case || null;
    const token = req.query.token;

    if (!pid || !phase || Number.isNaN(sessionNumber) || !token) {
      throw new HttpError(400, 'pid, phase, session, and token are required query parameters.');
    }

    if (!verifySurveyToken(pid, sessionNumber, phase, token)) {
      return textResponse(res, expiredHtml(), 410, { 'content-type': 'text/html' });
    }

    const { databases } = createAdminServices(req);
    const participant = await getParticipantByPid(databases, pid);
    if (!participant) {
      throw new HttpError(404, 'Participant not found.');
    }

    if (phase === 'pre') {
      await databases.updateDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.PARTICIPANTS,
        documentId: participant.$id,
        data: { pre_survey_completed: true, current_session: 1 },
      });
      return redirectResponse(res, buildReturnUrl(1));
    }

    if (phase === 'post') {
      const sessionLog = await getSessionLog(databases, participant.$id, sessionNumber);
      if (!sessionLog) {
        throw new HttpError(404, 'Session log not found for survey return.');
      }

      await databases.updateDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.SESSION_LOGS,
        documentId: sessionLog.$id,
        data: { survey_completed: true },
      });

      await databases.updateDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.PARTICIPANTS,
        documentId: participant.$id,
        data: {
          sosci_case_id: sosciCase,
          current_session: sessionNumber + 1,
          day2_completed: sessionNumber >= 2 ? true : participant.day2_completed,
        },
      });

      return redirectResponse(res, buildReturnUrl(sessionNumber + 1));
    }

    if (phase === 'day1exit') {
      await databases.updateDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.PARTICIPANTS,
        documentId: participant.$id,
        data: { day1_completed: true },
      });

      const code = participant.condition === 'A'
        ? process.env.PROLIFIC_COMPLETION_CODE_DAY1_A
        : process.env.PROLIFIC_COMPLETION_CODE_DAY1_B;

      return redirectResponse(res, prolificCompletionUrl(code));
    }

    if (phase === 'final') {
      await databases.updateDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.PARTICIPANTS,
        documentId: participant.$id,
        data: {
          day2_completed: true,
          study_completed: true,
        },
      });

      return redirectResponse(res, prolificCompletionUrl(process.env.PROLIFIC_COMPLETION_CODE_FINAL));
    }

    throw new HttpError(400, `Unsupported survey phase: ${phase}`);
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
