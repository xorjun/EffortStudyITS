import { createAdminServices } from '../../shared/clients.js';
import { buildSurveyToken, buildSurveyUrl } from '../../shared/survey.js';
import { getParticipantByUserId } from '../../shared/participants.js';
import { handleFunctionError, HttpError, jsonResponse, parseInteger, readJsonBody, requireMethod } from '../../shared/http.js';

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const body = readJsonBody(req);
    const userId = req.headers['x-appwrite-user-id'];
    const { databases } = createAdminServices(req);

    let participant = null;
    if (userId) {
      participant = await getParticipantByUserId(databases, userId);
    }

    const pid = body.pid || participant?.prolific_pid;
    const condition = body.condition || participant?.condition;
    const sessionNumber = parseInteger(body.session_number || body.sessionNumber, 'session_number');
    const phase = body.phase;

    if (!pid || !condition || !phase) {
      throw new HttpError(400, 'pid, condition, session_number, and phase are required.');
    }

    if (participant && participant.prolific_pid !== pid) {
      throw new HttpError(403, 'The requested participant does not match the authenticated user.');
    }

    return jsonResponse(res, {
      url: buildSurveyUrl({ pid, condition, sessionNumber, phase }),
      token: buildSurveyToken(pid, sessionNumber, phase),
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
