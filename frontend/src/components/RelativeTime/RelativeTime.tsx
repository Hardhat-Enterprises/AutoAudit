import React, { useEffect, useState } from 'react';
import { formatAbsoluteTooltipAEST } from '../../utils/helpers';
import { formatRelativeTime, toIsoTimestamp } from './relativeTimeFormat';
import type { RelativeTimeProps } from './RelativeTime.types';

export function RelativeTime({ value, className, tickMs = 60_000, locale }: RelativeTimeProps) {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), tickMs);
    return () => window.clearInterval(id);
  }, [tickMs]);

  const text = formatRelativeTime(value, now, locale);
  if (text === '-') {
    return <span className={className}>-</span>;
  }

  const iso = toIsoTimestamp(value);
  const title = formatAbsoluteTooltipAEST(value);

  return (
    <time dateTime={iso} title={title || undefined} className={className}>
      {text}
    </time>
  );
}
