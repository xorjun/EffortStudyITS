import { COLLECTIONS, CONDITION_LOCK_RETRIES, CONDITION_LOCK_RETRY_MS, CONDITION_LOCK_STALE_MS, CONDITION_VALUES, DATABASE_ID } from './constants.js';
import { HttpError, sleep } from './http.js';
import { participantDocumentPermissions } from './permissions.js';
import { ID, Query } from './sdk.js';

function nowIso() {
  return new Date().toISOString();
}

export async function getParticipantByPid(databases, prolificPid) {
  const result = await databases.listDocuments({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.PARTICIPANTS,
    queries: [Query.equal('prolific_pid', prolificPid), Query.limit(1)],
  });
  return result.documents[0] || null;
}

export async function getParticipantByUserId(databases, userId) {
  const result = await databases.listDocuments({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.PARTICIPANTS,
    queries: [Query.equal('appwrite_user_id', userId), Query.limit(1)],
  });
  return result.documents[0] || null;
}

async function getConditionCounts(databases, priorExp) {
  const perStratum = await databases.listDocuments({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.CONDITION_COUNTS,
    queries: [Query.equal('prior_exp', priorExp), Query.limit(2)],
  });

  if (perStratum.documents.length !== 2) {
    throw new HttpError(500, `Missing seeded condition_counts documents for ${priorExp}.`);
  }

  const allCounts = await databases.listDocuments({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.CONDITION_COUNTS,
    queries: [Query.limit(10)],
  });

  return {
    perStratum: perStratum.documents,
    all: allCounts.documents,
  };
}

async function acquireConditionLock(databases) {
  const lockId = 'condition_assignment';
  for (let attempt = 0; attempt < CONDITION_LOCK_RETRIES; attempt += 1) {
    try {
      await databases.createDocument({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.CONDITION_LOCKS,
        documentId: lockId,
        data: {
          lock_name: lockId,
          acquired_at: nowIso(),
        },
        permissions: [],
      });
      return lockId;
    } catch (error) {
      if (error?.code !== 409) {
        throw error;
      }

      try {
        const existing = await databases.getDocument({
          databaseId: DATABASE_ID,
          collectionId: COLLECTIONS.CONDITION_LOCKS,
          documentId: lockId,
        });
        if (Date.now() - Date.parse(existing.acquired_at) > CONDITION_LOCK_STALE_MS) {
          await databases.deleteDocument({
            databaseId: DATABASE_ID,
            collectionId: COLLECTIONS.CONDITION_LOCKS,
            documentId: lockId,
          }).catch(() => undefined);
          continue;
        }
      } catch {
        // Another execution may have released the lock already.
      }

      await sleep(CONDITION_LOCK_RETRY_MS);
    }
  }

  throw new HttpError(409, 'Condition assignment is busy. Please retry.');
}

async function releaseConditionLock(databases, lockId) {
  await databases.deleteDocument({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.CONDITION_LOCKS,
    documentId: lockId,
  }).catch(() => undefined);
}

function chooseCondition({ perStratum, all }) {
  const perCondition = new Map(perStratum.map((document) => [document.condition, document]));
  const a = perCondition.get('A');
  const b = perCondition.get('B');

  if (a.count !== b.count) {
    return a.count < b.count ? 'A' : 'B';
  }

  const totals = all.reduce((accumulator, document) => {
    accumulator[document.condition] = (accumulator[document.condition] || 0) + document.count;
    return accumulator;
  }, {});

  if ((totals.A || 0) !== (totals.B || 0)) {
    return (totals.A || 0) < (totals.B || 0) ? 'A' : 'B';
  }

  return CONDITION_VALUES[Math.floor(Math.random() * CONDITION_VALUES.length)];
}

export async function assignBalancedCondition(databases, priorExp) {
  const lockId = await acquireConditionLock(databases);
  try {
    const counts = await getConditionCounts(databases, priorExp);
    const chosenCondition = chooseCondition(counts);
    const chosenDocument = counts.perStratum.find((document) => document.condition === chosenCondition);

    await databases.incrementDocumentAttribute({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.CONDITION_COUNTS,
      documentId: chosenDocument.$id,
      attribute: 'count',
      value: 1,
    });

    return chosenCondition;
  } finally {
    await releaseConditionLock(databases, lockId);
  }
}

export async function determineCurrentSession(databases, participantId, fallbackCurrentSession = 1) {
  const result = await databases.listDocuments({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.SESSION_LOGS,
    queries: [
      Query.equal('participant_id', participantId),
      Query.orderAsc('session_number'),
      Query.limit(10),
    ],
  });

  if (result.documents.length === 0) {
    return fallbackCurrentSession;
  }

  for (const document of result.documents) {
    if (!document.completed_at || !document.survey_completed) {
      return document.session_number;
    }
  }

  return Math.max(fallbackCurrentSession, result.documents.at(-1).session_number + 1);
}

export async function createParticipant(databases, { prolificPid, priorExp, condition, userId }) {
  return databases.createDocument({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.PARTICIPANTS,
    documentId: ID.unique(),
    data: {
      prolific_pid: prolificPid,
      appwrite_user_id: userId,
      condition,
      prior_exp: priorExp,
      pre_survey_completed: false,
      day1_completed: false,
      day2_completed: false,
      study_completed: false,
      enrolled_at: nowIso(),
      current_session: 1,
    },
    permissions: participantDocumentPermissions(userId),
  });
}

export async function rebindParticipantUser(databases, participant, nextUserId) {
  await databases.updateDocument({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.PARTICIPANTS,
    documentId: participant.$id,
    data: {
      appwrite_user_id: nextUserId,
    },
    permissions: participantDocumentPermissions(nextUserId),
  });

  const sessionLogs = await databases.listDocuments({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.SESSION_LOGS,
    queries: [Query.equal('participant_id', participant.$id), Query.limit(25)],
  });

  await Promise.all(sessionLogs.documents.map((document) => databases.updateDocument({
    databaseId: DATABASE_ID,
    collectionId: COLLECTIONS.SESSION_LOGS,
    documentId: document.$id,
    data: {},
    permissions: participantDocumentPermissions(nextUserId),
  })));
}
