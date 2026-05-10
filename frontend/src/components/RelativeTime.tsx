import React, { useEffect, useState } from 'react';
import { formatAbsoluteTooltipAEST, parseDateForRelativeTime } from '../utils/helpers';

export type RelativeTimeLocale = Intl.LocalesArgument;

export type RelativeTimePreset = 'summary' | 'recentScanCell' | 'scansTableCell' | 'meta';

const PRESET_CLASS: Record<RelativeTimePreset, string> = {
  summary: 'font-semibold',
  recentScanCell: 'text-xs font-bold',
  scansTableCell: 'text-[13px] font-semibold text-[var(--text-primary)]',
  meta: 'mb-1 text-[13px] font-semibold',
};

export function relativeTimePresetClass(preset: RelativeTimePreset): string {
  return PRESET_CLASS[preset];
}

function mergePresetClass(
  preset: RelativeTimePreset | undefined,
  className: string | undefined
): string | undefined {
  const parts = [preset ? PRESET_CLASS[preset] : '', className].filter(Boolean);
  return parts.length ? parts.join(' ') : undefined;
}

export type RelativeTimeProps = {
  value: string | number | Date | null | undefined;
  className?: string;
  preset?: RelativeTimePreset;
  tickMs?: number;
  locale?: RelativeTimeLocale;
};

export function toIsoTimestamp(
  value: string | number | Date | null | undefined,
  referenceNowMs: number = Date.now()
): string | undefined {
  const d = parseDateForRelativeTime(value, referenceNowMs);
  return d?.toISOString();
}

export function formatRelativeTime(
  value: string | number | Date | null | undefined,
  now: Date = new Date(),
  locale?: RelativeTimeLocale
): string {
  const d = parseDateForRelativeTime(value, now.getTime());
  if (!d) return '-';

  const rtf = new Intl.RelativeTimeFormat(locale ?? undefined, { numeric: 'auto' });
  const diffMs = Math.min(0, d.getTime() - now.getTime());
  const diffSec = Math.trunc(diffMs / 1000);

  if (Math.abs(diffSec) < 60) return rtf.format(diffSec, 'second');
  const diffMin = Math.trunc(diffMs / 60_000);
  if (Math.abs(diffMin) < 60) return rtf.format(diffMin, 'minute');
  const diffHour = Math.trunc(diffMs / 3_600_000);
  if (Math.abs(diffHour) < 24) return rtf.format(diffHour, 'hour');
  const diffDay = Math.trunc(diffMs / 86_400_000);
  if (Math.abs(diffDay) < 7) return rtf.format(diffDay, 'day');
  const diffWeek = Math.trunc(diffMs / 604_800_000);
  if (Math.abs(diffWeek) < 4) return rtf.format(diffWeek, 'week');
  const diffMonth = Math.trunc(diffMs / 2_592_000_000);
  if (Math.abs(diffMonth) < 12) return rtf.format(diffMonth, 'month');
  const diffYear = Math.trunc(diffMs / 31_536_000_000);
  return rtf.format(diffYear, 'year');
}

const DEFAULT_TICK_MS = 1_000;

export function RelativeTime({
  value,
  className,
  preset,
  tickMs = DEFAULT_TICK_MS,
  locale,
}: RelativeTimeProps) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), tickMs);
    return () => window.clearInterval(id);
  }, [tickMs]);

  const text = formatRelativeTime(value, now, locale);
  const mergedClass = mergePresetClass(preset, className);
  if (text === '-') return <span className={mergedClass}>-</span>;

  const nowMs = now.getTime();
  const title = formatAbsoluteTooltipAEST(value);
  const iso = toIsoTimestamp(value, nowMs);
  return (
    <time dateTime={iso} title={title || undefined} className={mergedClass}>
      {text}
    </time>
  );
}
