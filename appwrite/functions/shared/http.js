export class HttpError extends Error {
  constructor(status, message, details = undefined) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.details = details;
  }
}

export function requireMethod(req, expectedMethod) {
  if (req.method !== expectedMethod) {
    throw new HttpError(405, `Method ${req.method} not allowed. Expected ${expectedMethod}.`);
  }
}

export function readJsonBody(req) {
  if (req.bodyJson && typeof req.bodyJson === 'object') {
    return req.bodyJson;
  }

  if (!req.bodyText) {
    return {};
  }

  try {
    return JSON.parse(req.bodyText);
  } catch {
    throw new HttpError(400, 'Request body must be valid JSON.');
  }
}

export function jsonResponse(res, data, status = 200, headers = {}) {
  return res.json(data, status, headers);
}

export function textResponse(res, body, status = 200, headers = {}) {
  return res.text(body, status, headers);
}

export function redirectResponse(res, url, status = 302) {
  return res.redirect(url, status);
}

export function parseInteger(value, fieldName) {
  const parsed = Number.parseInt(String(value), 10);
  if (Number.isNaN(parsed)) {
    throw new HttpError(400, `Field ${fieldName} must be an integer.`);
  }
  return parsed;
}

export function parseOptionalInteger(value, fallback = 0) {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }
  return Number.parseInt(String(value), 10);
}

export function parseOptionalBoolean(value, fallback = false) {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }

  if (typeof value === 'boolean') {
    return value;
  }

  const normalized = String(value).trim().toLowerCase();
  if (['true', '1', 'yes', 'on'].includes(normalized)) {
    return true;
  }
  if (['false', '0', 'no', 'off'].includes(normalized)) {
    return false;
  }

  return fallback;
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function normalizeArray(value) {
  return Array.isArray(value) ? value : [];
}

export function handleFunctionError(res, error, logger = console.error) {
  if (error instanceof HttpError) {
    logger(error.message, error.details || '');
    return jsonResponse(res, {
      error: error.message,
      details: error.details,
    }, error.status);
  }

  logger(error?.stack || error?.message || error);
  return jsonResponse(res, { error: 'Internal server error.' }, 500);
}
