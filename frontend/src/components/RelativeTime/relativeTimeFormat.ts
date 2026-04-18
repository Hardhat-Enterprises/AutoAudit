import { parseDateBestEffortForRelative } from '../../utils/helpers';

export type RelativeTimeLocale = Intl.LocalesArgument;

/** ISO string for HTML `dateTime` (UTC), using the same instant as relative text when strings are ambiguous. */
export function toIsoTimestamp(
  value: string | number | Date | null | undefined,
  referenceNowMs: number = Date.now()
): string | undefined {
  const d = parseDateBestEffortForRelative(value, referenceNowMs);
  return d?.toISOString();
}

/**
 * Locale-aware relative time (e.g. "5 minutes ago"). Uses best-effort parsing for timezone-less
 * timestamps so labels align with AEST display and do not read as future by mistake.
 * Uses truncation (not rounding) so units do not roll over early near boundaries.
 */
export function formatRelativeTime(
  value: string | number | Date | null | undefined,
  now: Date = new Date(),
  locale?: RelativeTimeLocale
): string {
  const d = parseDateBestEffortForRelative(value, now.getTime());
  if (!d) return '-';
  const rtf = new Intl.RelativeTimeFormat(locale ?? undefined, { numeric: 'auto' });
  // Never show future labels like "in 1 hour" for scan timestamps; clamp to "now".
  const diffMs = Math.min(0, d.getTime() - now.getTime());
  const diffSec = Math.trunc(diffMs / 1000);
  if (Math.abs(diffSec) < 60) {
    return rtf.format(diffSec, 'second');
  }
  const diffMin = Math.trunc(diffMs / 60_000);
  if (Math.abs(diffMin) < 60) {
    return rtf.format(diffMin, 'minute');
  }
  const diffHour = Math.trunc(diffMs / 3_600_000);
  if (Math.abs(diffHour) < 24) {
    return rtf.format(diffHour, 'hour');
  }
  const diffDay = Math.trunc(diffMs / 86_400_000);
  if (Math.abs(diffDay) < 7) {
    return rtf.format(diffDay, 'day');
  }
  const diffWeek = Math.trunc(diffMs / 604_800_000);
  if (Math.abs(diffWeek) < 4) {
    return rtf.format(diffWeek, 'week');
  }
  const diffMonth = Math.trunc(diffMs / 2_592_000_000);
  if (Math.abs(diffMonth) < 12) {
    return rtf.format(diffMonth, 'month');
  }
  const diffYear = Math.trunc(diffMs / 31_536_000_000);
  return rtf.format(diffYear, 'year');
}
