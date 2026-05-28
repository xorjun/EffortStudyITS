import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { assignBalancedCondition, createParticipant, determineCurrentSession, getParticipantByPid, getParticipantByUserId, rebindParticipantUser } from '../../shared/participants.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, readJsonBody, requireMethod } from '../../shared/http.js';

function normalizePriorExp(rawValue) {
  const value = String(rawValue || '').trim().toUpperCase();
  if (/^EXP_[012]$/.test(value)) {
    return value;
  }
  if (/^[012]$/.test(value)) {
    return `EXP_${value}`;
  }
  throw new HttpError(400, 'prior_exp must be one of EXP_0, EXP_1, or EXP_2.');
}

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

    const priorExp = normalizePriorExp(body.prior_exp || body.priorExp);
    const studyId = body.STUDY_ID || body.studyId || null;
    const prolificSessionId = body.SESSION_ID || body.sessionId || null;

    const { databases } = createAdminServices(req);
    const existingByUser = await getParticipantByUserId(databases, userId);
    if (existingByUser && existingByUser.prolific_pid !== prolificPid) {
      throw new HttpError(409, 'This Appwrite user is already bound to a different participant.');
    }

    let participant = await getParticipantByPid(databases, prolificPid);

    if (!participant) {
      const condition = await assignBalancedCondition(databases, priorExp);
      participant = await createParticipant(databases, {
        prolificPid,
        priorExp,
        condition,
        userId,
      });
    } else if (participant.appwrite_user_id !== userId) {
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
      token: null,
      studyId,
      prolificSessionId,
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
