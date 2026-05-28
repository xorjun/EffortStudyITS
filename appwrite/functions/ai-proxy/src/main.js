import fs from 'node:fs/promises';
import { createAdminServices } from '../../shared/clients.js';
import { requireAuthenticatedUser } from '../../shared/auth.js';
import { getParticipantByUserId } from '../../shared/participants.js';
import { COLLECTIONS, DATABASE_ID, MAX_AI_QUERIES_PER_SESSION } from '../../shared/constants.js';
import { handleFunctionError, HttpError, jsonResponse, normalizeArray, parseInteger, readJsonBody, requireMethod } from '../../shared/http.js';
import { ID, Query } from '../../shared/sdk.js';
import { participantDocumentPermissions } from '../../shared/permissions.js';

const BASE_SYSTEM_PROMPT = [
  'You are a tutoring assistant for a programming study.',
  'Never provide complete solutions.',
  'If you show code, keep each example to at most 8 lines.',
  'Prefer hints, questions, and targeted debugging guidance over direct answers.',
].join(' ');

function normalizeMessage(message) {
  if (!message || typeof message !== 'object') {
    return null;
  }

  const role = typeof message.role === 'string' ? message.role : 'user';
  let content = '';
  if (typeof message.content === 'string') {
    content = message.content;
  } else if (Array.isArray(message.content)) {
    content = message.content.map((part) => part?.text || '').join('\n');
  }

  if (!content.trim()) {
    return null;
  }

  return { role, content: content.slice(0, 4000) };
}

async function loadSessionContexts() {
  const raw = await fs.readFile(new URL('./session-contexts.json', import.meta.url), 'utf8');
  return JSON.parse(raw);
}

function extractResponseText(responseJson) {
  const content = responseJson?.choices?.[0]?.message?.content;
  if (typeof content === 'string') {
    return content;
  }
  if (Array.isArray(content)) {
    return content.map((part) => part?.text || '').join('\n');
  }
  return 'No response text returned by the language model.';
}

export default async ({ req, res, error }) => {
  try {
    requireMethod(req, 'POST');
    const { userId } = requireAuthenticatedUser(req);
    const body = readJsonBody(req);
    const sessionNumber = parseInteger(body.session_number || body.sessionNumber, 'session_number');
    const currentCode = String(body.current_code || body.currentCode || '').slice(0, 12000);
    const messages = normalizeArray(body.messages).map(normalizeMessage).filter(Boolean);

    const { databases } = createAdminServices(req);
    const participant = await getParticipantByUserId(databases, userId);
    if (!participant) {
      throw new HttpError(404, 'No participant is bound to the current user.');
    }
    if (participant.condition === 'B') {
      throw new HttpError(403, 'AI support is not available for this participant.');
    }

    const priorQueries = await databases.listDocuments({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.AI_QUERIES,
      queries: [
        Query.equal('participant_id', participant.$id),
        Query.equal('session_number', sessionNumber),
        Query.limit(MAX_AI_QUERIES_PER_SESSION + 1),
      ],
    });

    if (priorQueries.documents.length >= MAX_AI_QUERIES_PER_SESSION) {
      throw new HttpError(429, 'You have reached the maximum AI queries for this session.');
    }

    const sessionContexts = await loadSessionContexts();
    const sessionContext = sessionContexts[String(sessionNumber)]?.context || 'No additional session context is configured.';
    const systemPrompt = `${BASE_SYSTEM_PROMPT}\n\nSession context:\n${sessionContext}\n\nCurrent learner code:\n${currentCode || '[no code provided]'}`;
    const requestMessages = [{ role: 'system', content: systemPrompt }, ...messages];

    const llmResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${process.env.LLM_API_KEY}`,
      },
      body: JSON.stringify({
        model: process.env.LLM_MODEL,
        messages: requestMessages,
        temperature: 0.3,
      }),
    });

    if (!llmResponse.ok) {
      const failureBody = await llmResponse.text();
      throw new HttpError(502, 'The language model request failed.', failureBody);
    }

    const llmPayload = await llmResponse.json();
    const responseText = extractResponseText(llmPayload).slice(0, 5000);
    const queryText = (messages.at(-1)?.content || '').slice(0, 2000);
    const tokensUsed = llmPayload?.usage?.total_tokens || 0;

    await databases.createDocument({
      databaseId: DATABASE_ID,
      collectionId: COLLECTIONS.AI_QUERIES,
      documentId: ID.unique(),
      data: {
        participant_id: participant.$id,
        query_text: queryText,
        query_type: String(body.query_type || 'chat').slice(0, 16),
        response_text: responseText,
        response_accepted: false,
        code_copied: false,
        tokens_used: tokensUsed,
        session_number: sessionNumber,
        created_at: new Date().toISOString(),
      },
      permissions: participantDocumentPermissions(userId),
    });

    return jsonResponse(res, {
      responseText,
      tokensUsed,
      remainingQueries: MAX_AI_QUERIES_PER_SESSION - priorQueries.documents.length - 1,
    });
  } catch (caughtError) {
    return handleFunctionError(res, caughtError, (message, details) => error(String(message), details || ''));
  }
};
