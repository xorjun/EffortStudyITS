import { COLLECTIONS, DATABASE_ID } from './constants.js';
import { HttpError } from './http.js';
import { participantDocumentPermissions } from './permissions.js';
import { ID, Query } from './sdk.js';

function nowIso() {
  return new Date().toISOString();
}

export async function getSessionLog(databases, participantId, sessionNumber) {
  const result = await databases.listDocuments({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.SESSION_LOGS,
    queries: [
      Query.equal('participant_id', participantId),
      Query.equal('session_number', sessionNumber),
      Query.limit(1),
    ],
  });
  return result.documents[0] || null;
}

export async function guardPreviousSurvey(databases, participantId, sessionNumber) {
  if (sessionNumber <= 1) {
    return;
  }
  const previous = await getSessionLog(databases, participantId, sessionNumber - 1);
  if (previous && !previous.survey_completed) {
    throw new HttpError(403, 'Complete the previous survey before starting the next session.');
  }
}

export async function upsertSessionLog(databases, userId, participantId, sessionNumber, data = {}) {
  const existing = await getSessionLog(databases, participantId, sessionNumber);
  const payload = {
    participant_id: participantId,
    session_number: sessionNumber,
    started_at: data.started_at || nowIso(),
    ...data,
  };

  if (existing) {
    return databases.updateDocument({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.SESSION_LOGS,
      documentId: existing.$id,
      data: payload,
      permissions: participantDocumentPermissions(userId),
    });
  }

  return databases.createDocument({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.SESSION_LOGS,
    documentId: ID.unique(),
    data: payload,
    permissions: participantDocumentPermissions(userId),
  });
}
