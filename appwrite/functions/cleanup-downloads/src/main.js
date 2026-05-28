import { createAdminServices } from '../../shared/clients.js';
import { DOWNLOAD_BUCKET_ID } from '../../shared/constants.js';
import { handleFunctionError, jsonResponse } from '../../shared/http.js';
import { Query } from '../../shared/sdk.js';

export default async ({ req, res, error }) => {
  try {
    const { storage } = createAdminServices(req);
    const cutoff = new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString();
    let deletedCount = 0;
    let cursorAfter = null;

    while (true) {
      const queries = [Query.lessThan('$createdAt', cutoff), Query.limit(100)];
      if (cursorAfter) {
        queries.push(Query.cursorAfter(cursorAfter));
      }

      const page = await storage.listFiles({ bucketId: DOWNLOAD_BUCKET_ID, queries });
      if (page.files.length === 0) {
        break;
      }

      for (const file of page.files) {
        await storage.deleteFile({ bucketId: DOWNLOAD_BUCKET_ID, fileId: file.$id });
        deletedCount += 1;
      }

      if (page.files.length < 100) {
        break;
      }
      cursorAfter = page.files.at(-1).$id;
    }

    return jsonResponse(res, { deletedCount, cutoff });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
