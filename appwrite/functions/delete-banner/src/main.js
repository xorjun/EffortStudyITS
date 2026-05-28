import { createAdminServices } from '../../shared/clients.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, readJsonBody, requireMethod } from '../../shared/http.js';

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const body = readJsonBody(req);
    const bannerId = body.banner_id || body.bannerId;

    if (!bannerId) {
      throw new HttpError(400, 'banner_id is required.');
    }

    const { databases } = createAdminServices(req);
    await databases.deleteDocument({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.BANNERS,
      documentId: bannerId,
    });

    return jsonResponse(res, { success: true });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
