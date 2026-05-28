import { createAdminServices } from '../../shared/clients.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, jsonResponse, requireMethod } from '../../shared/http.js';
import { Query } from '../../shared/sdk.js';

function parseInputs(inputsJson) {
  try {
    const inputs = JSON.parse(inputsJson || '[]');
    return Array.isArray(inputs) ? inputs : [];
  } catch {
    return [];
  }
}

function serializeBanner(banner) {
  return {
    id: banner.$id,
    name: banner.name,
    message: banner.message,
    triggerPosition: banner.trigger_position,
    inputs: parseInputs(banner.inputs_json),
    triggerSessionFrom: banner.trigger_session_from,
    triggerSessionTo: banner.trigger_session_to,
    triggerAfterMinutes: banner.trigger_after_minutes,
    isActive: banner.is_active,
    isDismissable: banner.is_dismissable,
    blocksProgress: banner.blocks_progress,
    targetCondition: banner.target_condition,
    createdAt: banner.$createdAt,
    updatedAt: banner.$updatedAt,
  };
}

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const { databases } = createAdminServices(req);
    const banners = await databases.listDocuments({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.BANNERS,
      queries: [Query.limit(200)],
    });

    return jsonResponse(res, {
      banners: banners.documents.map(serializeBanner),
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
