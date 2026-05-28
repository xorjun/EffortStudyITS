import crypto from 'node:crypto';
import { ITS_BASE_URL } from './constants.js';

function currentHourBucket(date = new Date()) {
  return Math.floor(date.getTime() / 1000 / 3600);
}

export function buildSurveyToken(pid, sessionNumber, phase, hourBucket = currentHourBucket()) {
  const secret = process.env.SURVEY_LINK_SECRET;
  if (!secret) {
    throw new Error('SURVEY_LINK_SECRET is not configured.');
  }

  return crypto
    .createHmac('sha256', secret)
    .update([pid, sessionNumber, phase, hourBucket].join(':'))
    .digest('hex')
    .slice(0, 16);
}

export function verifySurveyToken(pid, sessionNumber, phase, token) {
  return token === buildSurveyToken(pid, sessionNumber, phase) || token === buildSurveyToken(pid, sessionNumber, phase, currentHourBucket() - 1);
}

export function buildSurveyUrl({ pid, condition, sessionNumber, phase }) {
  const baseUrl = process.env.SOSCI_BASE_URL;
  if (!baseUrl) {
    throw new Error('SOSCI_BASE_URL is not configured.');
  }

  const url = new URL(baseUrl);
  url.searchParams.set('pid', pid);
  url.searchParams.set('cond', condition);
  url.searchParams.set('session', String(sessionNumber));
  url.searchParams.set('phase', phase);
  url.searchParams.set('token', buildSurveyToken(pid, sessionNumber, phase));
  return url.toString();
}

export function buildReturnUrl(sessionNumber) {
  const url = new URL(ITS_BASE_URL);
  url.searchParams.set('session', String(sessionNumber));
  return url.toString();
}
