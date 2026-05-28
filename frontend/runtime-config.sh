#!/bin/sh
set -eu

cat > /usr/share/nginx/html/assets/runtime-config.json <<EOF
{
  "appwrite": {
    "endpoint": "${APPWRITE_ENDPOINT:-}",
    "projectId": "${APPWRITE_PROJECT_ID:-}",
    "databaseId": "${APPWRITE_DATABASE_ID:-study_db}",
    "downloadBucketId": "${APPWRITE_DOWNLOAD_BUCKET_ID:-download_zips}",
    "adminTeamId": "${APPWRITE_ADMIN_TEAM_ID:-admins}",
    "functions": {
      "authInit": "${APPWRITE_FUNCTION_AUTH_INIT_ID:-auth-init}",
      "sessionStart": "${APPWRITE_FUNCTION_SESSION_START_ID:-session-start}",
      "sessionComplete": "${APPWRITE_FUNCTION_SESSION_COMPLETE_ID:-session-complete}",
      "generateSurveyUrl": "${APPWRITE_FUNCTION_GENERATE_SURVEY_URL_ID:-generate-survey-url}",
      "aiProxy": "${APPWRITE_FUNCTION_AI_PROXY_ID:-ai-proxy}",
      "checkBanners": "${APPWRITE_FUNCTION_CHECK_BANNERS_ID:-check-banners}",
      "submitBannerResponse": "${APPWRITE_FUNCTION_SUBMIT_BANNER_RESPONSE_ID:-submit-banner-response}",
      "listBanners": "${APPWRITE_FUNCTION_LIST_BANNERS_ID:-list-banners}",
      "saveBanner": "${APPWRITE_FUNCTION_SAVE_BANNER_ID:-save-banner}",
      "deleteBanner": "${APPWRITE_FUNCTION_DELETE_BANNER_ID:-delete-banner}",
      "exportParticipants": "${APPWRITE_FUNCTION_EXPORT_PARTICIPANTS_ID:-export-participants}",
      "exportBannerResponses": "${APPWRITE_FUNCTION_EXPORT_BANNER_RESPONSES_ID:-export-banner-responses}",
      "getStudyConfig": "${APPWRITE_FUNCTION_GET_STUDY_CONFIG_ID:-get-study-config}",
      "saveStudyConfig": "${APPWRITE_FUNCTION_SAVE_STUDY_CONFIG_ID:-save-study-config}"
    }
  }
}
EOF
