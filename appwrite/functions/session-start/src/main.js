import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { getParticipantByUserId } from '../../shared/participants.js';
import { guardPreviousSurvey, upsertSessionLog } from '../../shared/sessions.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, parseInteger, readJsonBody, requireMethod } from '../../shared/http.js';

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const { userId } = requireAuthenticatedUser(req);
    const body = readJsonBody(req);
    const sessionNumber = parseInteger(body.session_number || body.sessionNumber, 'session_number');

    const { databases } = createAdminServices(req);
    const participant = await getParticipantByUserId(databases, userId);
    if (!participant) {
      throw new HttpError(404, 'No participant is bound to the current user.');
    }

    await guardPreviousSurvey(databases, participant.$id, sessionNumber);
    const sessionLog = await upsertSessionLog(databases, userId, participant.$id, sessionNumber, {
      started_at: new Date().toISOString(),
    });

    await databases.updateDocument({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.PARTICIPANTS,
      documentId: participant.$id,
      data: { current_session: sessionNumber },
    });

    return jsonResponse(res, {
      sessionLogId: sessionLog.$id,
      sessionNumber,
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
