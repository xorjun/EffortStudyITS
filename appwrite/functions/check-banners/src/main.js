import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { getParticipantByUserId } from '../../shared/participants.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, normalizeArray, parseInteger, parseOptionalInteger, readJsonBody, requireMethod } from '../../shared/http.js';
import { Query } from '../../shared/sdk.js';

function matchesTrigger(banner, firedEvents, elapsedMinutes) {
  switch (banner.trigger_position) {
    case 'session-arrival':
      return firedEvents.has('session-arrival');
    case 'first-code-run':
      return firedEvents.has('first-code-run') || firedEvents.has('code-run');
    case 'first-error':
      return firedEvents.has('first-error') || firedEvents.has('error');
    case 'first-hint-open':
      return firedEvents.has('first-hint-open') || firedEvents.has('hint-open');
    case 'time-based':
      return elapsedMinutes >= (banner.trigger_after_minutes || 0);
    default:
      return false;
  }
}

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const { userId } = requireAuthenticatedUser(req);
    const body = readJsonBody(req);
    const sessionNumber = parseInteger(body.session_number || body.sessionNumber, 'session_number');
    const elapsedMinutes = parseOptionalInteger(body.elapsed_minutes || body.elapsedMinutes, 0);
    const firedEvents = new Set(normalizeArray(body.fired_events || body.firedEvents).map((value) => String(value)));

    const { databases } = createAdminServices(req);
    const participant = await getParticipantByUserId(databases, userId);
    if (!participant) {
      throw new HttpError(404, 'No participant is bound to the current user.');
    }

    const [banners, existingResponses] = await Promise.all([
      databases.listDocuments({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.BANNERS,
        queries: [
          Query.equal('is_active', true),
          Query.lessThanEqual('trigger_session_from', sessionNumber),
          Query.greaterThanEqual('trigger_session_to', sessionNumber),
          Query.limit(100),
        ],
      }),
      databases.listDocuments({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.BANNER_RESPONSES,
        queries: [
          Query.equal('participant_id', participant.$id),
          Query.equal('session_number', sessionNumber),
          Query.limit(100),
        ],
      }),
    ]);

    const shownBannerIds = new Set(existingResponses.documents.map((document) => document.banner_id));

    const availableBanners = banners.documents
      .filter((banner) => banner.target_condition === 'all' || banner.target_condition === participant.condition)
      .filter((banner) => !shownBannerIds.has(banner.$id))
      .filter((banner) => matchesTrigger(banner, firedEvents, elapsedMinutes))
      .map((banner) => ({
        id: banner.$id,
        name: banner.name,
        message: banner.message,
        triggerPosition: banner.trigger_position,
        blocksProgress: banner.blocks_progress,
        isDismissable: banner.is_dismissable,
        shownAt: new Date().toISOString(),
        inputs: JSON.parse(banner.inputs_json),
      }));

    return jsonResponse(res, { banners: availableBanners });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
