import { createAdminServices } from '../../shared/clients.js';
import { COLLECTIONS, DATABASE_ID } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, parseInteger, parseOptionalBoolean, parseOptionalInteger, readJsonBody, requireMethod } from '../../shared/http.js';
import { ID } from '../../shared/sdk.js';
import { adminTeamDocumentPermissions } from '../../shared/permissions.js';

const VALID_TRIGGER_POSITIONS = new Set([
  'session-arrival',
  'first-code-run',
  'first-error',
  'first-hint-open',
  'time-based',
]);

const VALID_TARGET_CONDITIONS = new Set(['A', 'B', 'all']);

function parseInputs(value) {
  if (Array.isArray(value)) {
    return value;
  }

  if (!value) {
    return [];
  }

  try {
    const parsed = JSON.parse(String(value));
    if (!Array.isArray(parsed)) {
      throw new Error('inputs must be an array');
    }
    return parsed;
  } catch {
    throw new HttpError(400, 'inputs_json must be a valid JSON array.');
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
    const body = readJsonBody(req);
    const bannerId = body.banner_id || body.bannerId;
    const name = String(body.name || '').trim().slice(0, 100);
    const message = String(body.message || '').trim().slice(0, 1000);
    const triggerPosition = String(body.trigger_position || body.triggerPosition || '').trim();
    const targetCondition = String(body.target_condition || body.targetCondition || '').trim();
    const triggerSessionFrom = parseInteger(body.trigger_session_from ?? body.triggerSessionFrom, 'trigger_session_from');
    const triggerSessionTo = parseInteger(body.trigger_session_to ?? body.triggerSessionTo, 'trigger_session_to');
    const triggerAfterMinutes = parseOptionalInteger(body.trigger_after_minutes ?? body.triggerAfterMinutes, 0);
    const inputs = parseInputs(body.inputs ?? body.inputs_json ?? body.inputsJson);

    if (!name || !message) {
      throw new HttpError(400, 'name and message are required.');
    }
    if (!VALID_TRIGGER_POSITIONS.has(triggerPosition)) {
      throw new HttpError(400, 'trigger_position is invalid.');
    }
    if (!VALID_TARGET_CONDITIONS.has(targetCondition)) {
      throw new HttpError(400, 'target_condition is invalid.');
    }
    if (triggerSessionTo < triggerSessionFrom) {
      throw new HttpError(400, 'trigger_session_to must be greater than or equal to trigger_session_from.');
    }

    const payload = {
      name,
      message,
      trigger_position: triggerPosition,
      inputs_json: JSON.stringify(inputs).slice(0, 5000),
      trigger_session_from: triggerSessionFrom,
      trigger_session_to: triggerSessionTo,
      trigger_after_minutes: triggerAfterMinutes,
      is_active: parseOptionalBoolean(body.is_active ?? body.isActive, false),
      is_dismissable: parseOptionalBoolean(body.is_dismissable ?? body.isDismissable, true),
      blocks_progress: parseOptionalBoolean(body.blocks_progress ?? body.blocksProgress, false),
      target_condition: targetCondition,
    };

    const { databases } = createAdminServices(req);
    const document = bannerId
      ? await databases.updateDocument({
          databaseId: DATABASE_ID,
          collectionId: COLLECTIONS.BANNERS,
          documentId: bannerId,
          data: payload,
          permissions: adminTeamDocumentPermissions(),
        })
      : await databases.createDocument({
          databaseId: DATABASE_ID,
          collectionId: COLLECTIONS.BANNERS,
          documentId: ID.unique(),
          data: payload,
          permissions: adminTeamDocumentPermissions(),
        });

    return jsonResponse(res, { banner: serializeBanner(document) });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
