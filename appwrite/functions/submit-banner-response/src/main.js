import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { getParticipantByUserId } from '../../shared/participants.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, parseInteger, parseOptionalBoolean, readJsonBody, requireMethod } from '../../shared/http.js';
import { ID, Query } from '../../shared/sdk.js';
import { participantDocumentPermissions } from '../../shared/permissions.js';

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const { userId } = requireAuthenticatedUser(req);
    const body = readJsonBody(req);
    const bannerId = body.banner_id || body.bannerId;
    const triggerEvent = body.trigger_event || body.triggerEvent || 'manual';
    const shownAt = body.shown_at || body.shownAt;
    const sessionNumber = parseInteger(body.session_number || body.sessionNumber, 'session_number');
    const responseData = body.response_data || body.responseData || {};

    if (!bannerId || !shownAt) {
      throw new HttpError(400, 'banner_id and shown_at are required.');
    }

    const { databases } = createAdminServices(req);
    const participant = await getParticipantByUserId(databases, userId);
    if (!participant) {
      throw new HttpError(404, 'No participant is bound to the current user.');
    }

    const existing = await databases.listDocuments({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.BANNER_RESPONSES,
      queries: [
        Query.equal('banner_id', bannerId),
        Query.equal('participant_id', participant.$id),
        Query.equal('session_number', sessionNumber),
        Query.limit(1),
      ],
    });

    if (existing.documents.length > 0) {
      return jsonResponse(res, { success: true, documentId: existing.documents[0].$id });
    }

    const respondedAt = new Date();
    const secondsToRespond = Math.max(0, (respondedAt.getTime() - Date.parse(shownAt)) / 1000);

    const document = await databases.createDocument({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.BANNER_RESPONSES,
      documentId: ID.unique(),
      data: {
        banner_id: bannerId,
        participant_id: participant.$id,
        trigger_event: String(triggerEvent).slice(0, 32),
        response_data: JSON.stringify(responseData).slice(0, 5000),
        was_dismissed: parseOptionalBoolean(body.was_dismissed ?? body.wasDismissed, false),
        session_number: sessionNumber,
        shown_at: shownAt,
        responded_at: respondedAt.toISOString(),
        seconds_to_respond: secondsToRespond,
      },
      permissions: participantDocumentPermissions(userId),
    });

    return jsonResponse(res, { success: true, documentId: document.$id });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
