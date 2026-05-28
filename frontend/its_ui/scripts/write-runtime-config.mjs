import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputPath = path.resolve(__dirname, '../src/assets/runtime-config.json');

const runtimeConfig = {
  appwrite: {
    endpoint: process.env.APPWRITE_ENDPOINT || '',
    projectId: process.env.APPWRITE_PROJECT_ID || '',
    databaseId: process.env.APPWRITE_DATABASE_ID || 'study_db',
    downloadBucketId: process.env.APPWRITE_DOWNLOAD_BUCKET_ID || 'download_zips',
    adminTeamId: process.env.APPWRITE_ADMIN_TEAM_ID || 'admins',
    functions: {
      authInit: process.env.APPWRITE_FUNCTION_AUTH_INIT_ID || 'auth-init',
      sessionStart: process.env.APPWRITE_FUNCTION_SESSION_START_ID || 'session-start',
      sessionComplete: process.env.APPWRITE_FUNCTION_SESSION_COMPLETE_ID || 'session-complete',
      generateSurveyUrl: process.env.APPWRITE_FUNCTION_GENERATE_SURVEY_URL_ID || 'generate-survey-url',
      aiProxy: process.env.APPWRITE_FUNCTION_AI_PROXY_ID || 'ai-proxy',
      checkBanners: process.env.APPWRITE_FUNCTION_CHECK_BANNERS_ID || 'check-banners',
      submitBannerResponse: process.env.APPWRITE_FUNCTION_SUBMIT_BANNER_RESPONSE_ID || 'submit-banner-response',
      listBanners: process.env.APPWRITE_FUNCTION_LIST_BANNERS_ID || 'list-banners',
      saveBanner: process.env.APPWRITE_FUNCTION_SAVE_BANNER_ID || 'save-banner',
      deleteBanner: process.env.APPWRITE_FUNCTION_DELETE_BANNER_ID || 'delete-banner',
      exportParticipants: process.env.APPWRITE_FUNCTION_EXPORT_PARTICIPANTS_ID || 'export-participants',
      exportBannerResponses: process.env.APPWRITE_FUNCTION_EXPORT_BANNER_RESPONSES_ID || 'export-banner-responses',
      getStudyConfig: process.env.APPWRITE_FUNCTION_GET_STUDY_CONFIG_ID || 'get-study-config',
      saveStudyConfig: process.env.APPWRITE_FUNCTION_SAVE_STUDY_CONFIG_ID || 'save-study-config',
    },
  },
};

await fs.writeFile(outputPath, `${JSON.stringify(runtimeConfig, null, 2)}\n`, 'utf8');
console.log(`Wrote runtime Appwrite config to ${outputPath}`);
