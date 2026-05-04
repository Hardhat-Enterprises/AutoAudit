import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { formatRelativeTime, toIsoTimestamp } from './RelativeTime';

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
    expect(formatRelativeTime(past, new Date('2026-04-05T12:00:00.000Z'), 'en')).toMatch(
      /30 seconds ago/
    );
  });

  it('uses minutes when under an hour', () => {
    const past = new Date('2026-04-05T11:55:00.000Z');
    expect(formatRelativeTime(past, new Date('2026-04-05T12:00:00.000Z'), 'en')).toMatch(
      /5 minutes ago/
    );
  });

  it('returns "-" for invalid input', () => {
    expect(formatRelativeTime(null, new Date('2026-04-05T12:00:00.000Z'))).toBe('-');
  });

  it('clamps to "now" when the instant is after now (avoids "in X" for future instants)', () => {
    const now = new Date('2026-04-18T10:00:00.000Z');
    const future = new Date('2026-04-18T11:00:00.000Z');
    expect(formatRelativeTime(future, now, 'en')).toMatch(/^now$/i);
  });
});

describe('toIsoTimestamp', () => {
  it('normalizes timezone-less ISO strings when unambiguous (reference in the future)', () => {
    const ref = new Date('2027-06-01T00:00:00.000Z').getTime();
    expect(toIsoTimestamp('2026-01-17T05:09:13', ref)).toBe('2026-01-17T05:09:13.000Z');
  });
});

describe('ambiguous timezone-less timestamps', () => {
  it('prefers a past interpretation for relative time (avoids false "in X hours")', () => {
    const now = new Date('2026-04-18T12:00:00.000Z');
    const naive = '2026-04-18T21:33:33';
    const text = formatRelativeTime(naive, now, 'en');
    expect(text).not.toMatch(/^in\b/);
    expect(text).toMatch(/\bago\b/);
  });
});
