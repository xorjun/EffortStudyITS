import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { getParticipantByUserId } from '../../shared/participants.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, parseInteger, readJsonBody, requireMethod } from '../../shared/http.js';
import { ID } from '../../shared/sdk.js';
import { participantDocumentPermissions } from '../../shared/permissions.js';

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const { userId } = requireAuthenticatedUser(req);
    const body = readJsonBody(req);
    const { databases } = createAdminServices(req);
    const participant = await getParticipantByUserId(databases, userId);
    if (!participant) {
      throw new HttpError(404, 'No participant is bound to the current user.');
    }

    const document = await databases.createDocument({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.AI_QUERIES,
      documentId: ID.unique(),
      data: {
        participant_id: participant.$id,
        query_text: String(body.query_text || body.queryText || '').slice(0, 2000),
        query_type: String(body.query_type || body.queryType || 'chat').slice(0, 16),
        response_text: String(body.response_text || body.responseText || '').slice(0, 5000),
        response_accepted: Boolean(body.response_accepted || body.responseAccepted),
        code_copied: Boolean(body.code_copied || body.codeCopied),
        tokens_used: parseInteger(body.tokens_used || body.tokensUsed || 0, 'tokens_used'),
        session_number: parseInteger(body.session_number || body.sessionNumber, 'session_number'),
        created_at: new Date().toISOString(),
      },
      permissions: participantDocumentPermissions(userId),
    });

    return jsonResponse(res, { documentId: document.$id });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
