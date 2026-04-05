import { parseDateAssumingUTC } from '../../utils/helpers';

export type RelativeTimeLocale = Intl.LocalesArgument;

function resolveInstant(value: string | number | Date | null | undefined): Date | null {
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }
  return parseDateAssumingUTC(value);
}

/** ISO string for HTML `dateTime` (UTC), using the same parsing rules as other timestamp formatters. */
export function toIsoTimestamp(value: string | number | Date | null | undefined): string | undefined {
  const d = resolveInstant(value);
  return d?.toISOString();
}

/**
 * Locale-aware relative time (e.g. "5 minutes ago") using the same UTC parsing rules as AEST/GMT formatters.
 */
export function formatRelativeTime(
  value: string | number | Date | null | undefined,
  now: Date = new Date(),
  locale?: RelativeTimeLocale
): string {
  const d = resolveInstant(value);
  if (!d) return '-';

  const rtf = new Intl.RelativeTimeFormat(locale ?? undefined, { numeric: 'auto' });
  const diffMs = d.getTime() - now.getTime();
  const diffSec = Math.round(diffMs / 1000);

  if (Math.abs(diffSec) < 60) {
    return rtf.format(diffSec, 'second');
  }

  const diffMin = Math.round(diffMs / 60_000);
  if (Math.abs(diffMin) < 60) {
    return rtf.format(diffMin, 'minute');
  }

  const diffHour = Math.round(diffMs / 3_600_000);
  if (Math.abs(diffHour) < 24) {
    return rtf.format(diffHour, 'hour');
  }

  const diffDay = Math.round(diffMs / 86_400_000);
  if (Math.abs(diffDay) < 7) {
    return rtf.format(diffDay, 'day');
  }

  const diffWeek = Math.round(diffMs / 604_800_000);
  if (Math.abs(diffWeek) < 4) {
    return rtf.format(diffWeek, 'week');
  }

  const diffMonth = Math.round(diffMs / 2_592_000_000);
  if (Math.abs(diffMonth) < 12) {
    return rtf.format(diffMonth, 'month');
  }

  const diffYear = Math.round(diffMs / 31_536_000_000);
  return rtf.format(diffYear, 'year');
}
