import { HttpError } from './http.js';

export function requireAuthenticatedUser(req) {
  const userId = req.headers['x-appwrite-user-id'];
  const userJwt = req.headers['x-appwrite-user-jwt'];

  if (!userId || !userJwt) {
    throw new HttpError(401, 'This function requires an authenticated Appwrite user session.');
  }

  return { userId, userJwt };
}
