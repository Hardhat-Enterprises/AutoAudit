// Helper functions for the app
// Created on: Nov 2024

export const validateEmail = (email) => {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return re.test(email);
};

export const formatDate = (date) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(date).toLocaleDateString(undefined, options);
};

// Standardized GMT/UTC date+time formatting for consistent display across users/machines.
// - Date: "DD Mon YYYY"
// - Time: "h:mm:ss.SSS AM GMT"
function parseDateAssumingUTC(value) {
  if (!value) return null;
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;

  // If backend returns an ISO string WITHOUT timezone (e.g. "2026-01-17T05:09:13"),
  // browsers may treat it as local time. We treat such values as UTC to keep
  // timestamps globally consistent.
  if (typeof value === 'string') {
    const s = value.trim();
    const hasTz = /([zZ]|[+-]\d{2}:\d{2})$/.test(s);
    const looksIso = /^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(:\d{2}(\.\d{1,6})?)?$/.test(s);
    const normalized = !hasTz && looksIso ? `${s.replace(' ', 'T')}Z` : s;
    const d = new Date(normalized);
    return Number.isNaN(d.getTime()) ? null : d;
  }

  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

export const formatDateGMT = (dateString) => {
  const d = parseDateAssumingUTC(dateString);
  if (!d) return '-';
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(d);
};

export const formatTimeGMT = (dateString) => {
  const d = parseDateAssumingUTC(dateString);
  if (!d) return '-';
  const timeCore = new Intl.DateTimeFormat('en-GB', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3,
    hour12: true,
    timeZone: 'UTC',
  }).format(d);
  return `${timeCore} GMT`;
};

export const formatDateTimePartsGMT = (dateString) => {
  const date = formatDateGMT(dateString);
  if (date === '-') return { date: '-', time: '-' };
  return { date, time: formatTimeGMT(dateString) };
};

// AEST display (fixed UTC+10). We intentionally use Australia/Brisbane because it
// does not observe DST; label remains "AEST" year-round as requested.
const AEST_IANA_TZ = 'Australia/Brisbane';

export const formatDateAEST = (dateString) => {
  const d = parseDateAssumingUTC(dateString);
  if (!d) return '-';
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: AEST_IANA_TZ,
  }).format(d);
};

export const formatTimeAEST = (dateString) => {
  const d = parseDateAssumingUTC(dateString);
  if (!d) return '-';
  const timeCore = new Intl.DateTimeFormat('en-GB', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: AEST_IANA_TZ,
  }).format(d);
  return `${timeCore} AEST`;
};

export const formatDateTimePartsAEST = (dateString) => {
  const date = formatDateAEST(dateString);
  if (date === '-') return { date: '-', time: '-' };
  return { date, time: formatTimeAEST(dateString) };
};

// Simple utility for string truncation
export const truncateString = (str, maxLength) => {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength) + '...';
};