import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { formatRelativeTime, toIsoTimestamp } from './relativeTimeFormat';

describe('formatRelativeTime', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-04-05T12:00:00.000Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('uses seconds for very recent timestamps', () => {
    const past = new Date('2026-04-05T11:59:30.000Z');
    expect(formatRelativeTime(past, new Date('2026-04-05T12:00:00.000Z'), 'en')).toMatch(/30 seconds ago/);
  });

  it('uses minutes when under an hour', () => {
    const past = new Date('2026-04-05T11:55:00.000Z');
    expect(formatRelativeTime(past, new Date('2026-04-05T12:00:00.000Z'), 'en')).toMatch(/5 minutes ago/);
  });

  it('returns "-" for invalid input', () => {
    expect(formatRelativeTime(null, new Date('2026-04-05T12:00:00.000Z'))).toBe('-');
  });
});

describe('toIsoTimestamp', () => {
  it('normalizes timezone-less ISO strings as UTC', () => {
    expect(toIsoTimestamp('2026-01-17T05:09:13')).toBe('2026-01-17T05:09:13.000Z');
  });
});
