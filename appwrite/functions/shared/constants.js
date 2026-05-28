export const DATABASE_ID = process.env.APPWRITE_DATABASE_ID || 'study_db';
export const DOWNLOAD_BUCKET_ID = process.env.APPWRITE_DOWNLOAD_BUCKET_ID || 'download_zips';
export const ADMIN_TEAM_ID = process.env.APPWRITE_ADMIN_TEAM_ID || 'admins';
export const ITS_BASE_URL = process.env.ITS_BASE_URL || 'http://localhost:8080';
export const MAX_AI_QUERIES_PER_SESSION = 20;
export const CONDITION_LOCK_RETRIES = 3;
export const CONDITION_LOCK_RETRY_MS = 50;
export const CONDITION_LOCK_STALE_MS = 5000;

export const COLLECTIONS = {
  PARTICIPANTS: 'participants',
  SESSION_LOGS: 'session_logs',
  TELEMETRY_EVENTS: 'telemetry_events',
  AI_QUERIES: 'ai_queries',
  HINT_OPENS: 'hint_opens',
  BANNERS: 'banners',
  BANNER_RESPONSES: 'banner_responses',
  CONDITION_COUNTS: 'condition_counts',
  CONDITION_LOCKS: 'condition_locks',
};

export const CONDITION_VALUES = ['A', 'B'];
