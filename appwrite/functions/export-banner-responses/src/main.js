import { createAdminServices } from '../../shared/clients.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { toCsv } from '../../shared/csv.js';
import { handleFunctionError, HttpError, readJsonBody, requireMethod, textResponse } from '../../shared/http.js';
import { Query } from '../../shared/sdk.js';

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const body = readJsonBody(req);
    const bannerId = body.banner_id || body.bannerId;
    if (!bannerId) {
      throw new HttpError(400, 'banner_id is required.');
    }

    const { databases } = createAdminServices(req);
    const [banner, responses, participants] = await Promise.all([
      databases.getDocument({ databaseId: DATABASE_ID, collectionId: COLLECTIONS.BANNERS, documentId: bannerId }),
      databases.listDocuments({
        databaseId: DATABASE_ID,
        collectionId: COLLECTIONS.BANNER_RESPONSES,
        queries: [Query.equal('banner_id', bannerId), Query.limit(1000)],
      }),
      databases.listDocuments({ databaseId: DATABASE_ID, collectionId: COLLECTIONS.PARTICIPANTS, queries: [Query.limit(500)] }),
    ]);

    const participantMap = new Map(participants.documents.map((participant) => [participant.$id, participant]));
    const inputs = JSON.parse(banner.inputs_json);
    const inputHeaders = inputs.map((input, index) => `${input.type}_${index}`);

    const rows = [[
      'participant_id_anon',
      'condition',
      'session_number',
      'trigger_event',
      'seconds_to_respond',
      'was_dismissed',
      ...inputHeaders,
    ]];

    for (const response of responses.documents) {
      const participant = participantMap.get(response.participant_id);
      const parsedResponse = JSON.parse(response.response_data || '{}');
      rows.push([
        response.participant_id.slice(0, 8),
        participant?.condition || '',
        response.session_number,
        response.trigger_event,
        response.seconds_to_respond,
        response.was_dismissed,
        ...inputs.map((_, index) => parsedResponse[String(index)] ?? ''),
      ]);
    }

    return textResponse(res, toCsv(rows), 200, {
      'content-type': 'text/csv; charset=utf-8',
      'content-disposition': `attachment; filename="banner-${bannerId}.csv"`,
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
