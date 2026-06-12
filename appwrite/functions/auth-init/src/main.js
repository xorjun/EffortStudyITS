import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { assignBalancedCondition, createParticipant, determineCurrentSession, getParticipantByPid, getParticipantByUserId, rebindParticipantUser } from '../../shared/participants.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, readJsonBody, requireMethod } from '../../shared/http.js';

function normalizePid(body) {
  return body.prolific_pid || body.prolificPid || body.PROLIFIC_PID;
}

export default async ({ req, res, log, error }) => {
  try {
    requireMethod(req, 'POST');
    const { userId, userJwt } = requireAuthenticatedUser(req);
    const body = readJsonBody(req);
    const prolificPid = normalizePid(body);

    if (!prolificPid) {
      throw new HttpError(400, 'PROLIFIC_PID is required.');
    }

    const studyId = body.STUDY_ID || body.studyId || null;
    const prolificSessionId = body.SESSION_ID || body.sessionId || null;

    const { databases } = createAdminServices(req);

    // The Prolific PID is the canonical identity. The caller is expected to
    // have created an Appwrite account whose userId matches this PID (or a
    // deterministic email/password derived from it). We re-bind that
    // existing user to the participant document below.
    const existingByUser = await getParticipantByUserId(databases, userId);
    if (existingByUser && existingByUser.prolific_pid !== prolificPid) {
      throw new HttpError(409, 'This Appwrite user is already bound to a different participant.');
    }

    let participant = await getParticipantByPid(databases, prolificPid);

    if (!participant) {
      const condition = await assignBalancedCondition(databases);
      participant = await createParticipant(databases, {
        prolificPid,
        condition,
        userId,
      });
    } else if (participant.appwrite_user_id !== userId) {
      // Same PID on a new device / cleared session: rebind the Appwrite
      // user to the existing participant record so the PID stays the
      // single source of identity across all pipeline components.
      await rebindParticipantUser(databases, participant, userId);
      participant = await databases.getDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.PARTICIPANTS,
        documentId: participant.$id,
      });
    }

    const currentSession = await determineCurrentSession(databases, participant.$id, participant.current_session || 1);
    if (participant.current_session !== currentSession) {
      participant = await databases.updateDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.PARTICIPANTS,
        documentId: participant.$id,
        data: { current_session: currentSession },
      });
    }

    return jsonResponse(res, {
      participantId: participant.$id,
      participantUserId: userId,
      condition: participant.condition,
      currentSession,
      // Legacy field kept for backward compatibility with the existing Angular
      // client. New clients should read participantJwt below.
      token: null,
      // The session JWT echoed back from the caller's request. Subsequent
      // function calls can use this directly to authenticate as the
      // participant. Additive field; the legacy path is preserved.
      participantJwt: userJwt || null,
      studyId,
      prolificSessionId,
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
