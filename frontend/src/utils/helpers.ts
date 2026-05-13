// Helper functions for the app
// Created on: Nov 2024

export const validateEmail = (email: string): boolean => {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return re.test(email);
};

export const formatDate = (date: string | number | Date): string => {
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(date).toLocaleDateString(undefined, options);
};

// Standardized GMT/UTC date+time formatting for consistent display across users/machines.
// - Date: "DD Mon YYYY"
// - Time: "h:mm:ss.SSS AM GMT"
function parseDateAssumingUTC(value: string | number | Date | null | undefined): Date | null {
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

function parseDateAssumingLocal(value: string | number | Date | null | undefined): Date | null {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function parseDateForRelativeTime(
  value: string | number | Date | null | undefined,
  nowMs: number
): Date | null {
  const utcDate = parseDateAssumingUTC(value);
  if (!utcDate) return null;
  if (typeof value !== 'string') return utcDate;

  const raw = value.trim();
  const hasTz = /([zZ]|[+-]\d{2}:\d{2})$/.test(raw);
  if (hasTz) return utcDate;

  const candidates: Date[] = [utcDate];
  const localDate = parseDateAssumingLocal(raw);
  if (localDate) candidates.push(localDate);

  const looksIso = /^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(:\d{2}(\.\d{1,6})?)?$/.test(raw);
  if (looksIso) {
    const aestCandidate = new Date(`${raw.replace(' ', 'T')}+10:00`);
    if (!Number.isNaN(aestCandidate.getTime())) candidates.push(aestCandidate);
  }

  let bestPast: Date | null = null;
  let bestPastDiff = Number.POSITIVE_INFINITY;
  let bestAny: Date = candidates[0];
  let bestAnyAbsDiff = Math.abs(nowMs - candidates[0].getTime());

  for (const candidate of candidates) {
    const diff = nowMs - candidate.getTime();
    const absDiff = Math.abs(diff);
    if (diff >= 0 && diff < bestPastDiff) {
      bestPast = candidate;
      bestPastDiff = diff;
    }
    if (absDiff < bestAnyAbsDiff) {
      bestAny = candidate;
      bestAnyAbsDiff = absDiff;
    }
  }

  return bestPast ?? bestAny;
}

export const formatDateGMT = (dateString: string | number | Date | null | undefined): string => {
  const d = parseDateAssumingUTC(dateString);
  if (!d) return '-';
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(d);
};

export const formatTimeGMT = (dateString: string | number | Date | null | undefined): string => {
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

type DateTimeParts = {
  date: string;
  time: string;
}

export const formatDateTimePartsGMT = (dateString: string | number | Date | null | undefined): DateTimeParts => {
  const date = formatDateGMT(dateString);
  if (date === '-') return { date: '-', time: '-' };
  return { date, time: formatTimeGMT(dateString) };
};

// AEST display (fixed UTC+10). We intentionally use Australia/Brisbane because it
// does not observe DST; label remains "AEST" year-round as requested.
const AEST_IANA_TZ = 'Australia/Brisbane';

export const formatDateAEST = (dateString: string | number | Date | null | undefined): string => {
  const d = parseDateAssumingUTC(dateString);
  if (!d) return '-';
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: AEST_IANA_TZ,
  }).format(d);
};

export const formatTimeAEST = (dateString: string | number | Date | null | undefined): string => {
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

export const formatAbsoluteTooltipAEST = (
  dateString: string | number | Date | null | undefined
): string => {
  const date = formatDateAEST(dateString);
  if (date === '-') return '';
  return `${date} ${formatTimeAEST(dateString)}`;
};

export const formatDateTimePartsAEST = (dateString: string | number | Date | null | undefined): DateTimeParts => {
  const date = formatDateAEST(dateString);
  if (date === '-') return { date: '-', time: '-' };
  return { date, time: formatTimeAEST(dateString) };
};

// Simple utility for string truncation
export const truncateString = (str: string, maxLength: number): string => {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength) + '...';
};