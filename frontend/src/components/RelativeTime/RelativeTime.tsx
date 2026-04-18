import React, { useEffect, useState } from 'react';
import { formatAbsoluteTooltipAEST } from '../../utils/helpers';
import { formatRelativeTime, toIsoTimestamp } from './relativeTimeFormat';
import type { RelativeTimeProps } from './RelativeTime.types';

/** Default tick keeps second-level labels accurate (see formatRelativeTime). */
const DEFAULT_TICK_MS = 1_000;

export function RelativeTime({
  value,
  className,
  tickMs = DEFAULT_TICK_MS,
  locale,
}: RelativeTimeProps) {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), tickMs);
    return () => window.clearInterval(id);
  }, [tickMs]);
  const text = formatRelativeTime(value, now, locale);
  if (text === '-') {
    return <span className={className}>-</span>;
  }
  const nowMs = now.getTime();
  const title = formatAbsoluteTooltipAEST(value);
  const iso = toIsoTimestamp(value, nowMs);
  return (
    <time dateTime={iso} title={title || undefined} className={className}>
      {text}
    </time>
  );
}
