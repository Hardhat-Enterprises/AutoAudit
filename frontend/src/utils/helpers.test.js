import { describe, it, expect } from 'vitest';
import {
  validateEmail,
  formatDateGMT,
  formatTimeGMT,
  formatDateTimePartsGMT,
  formatDateAEST,
  formatTimeAEST,
  formatDateTimePartsAEST,
  truncateString,
} from './helpers';

describe('validateEmail', () => {
  it('accepts a standard email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });
  it('accepts email with dots, underscores and subdomains', () => {
    expect(validateEmail('user.name@sub.example.co.uk')).toBe(true);
  });
  it('accepts email with plus addressing', () => {
    expect(validateEmail('user+tag@example.com')).toBe(true);
  });
  it('rejects email missing @', () => {
    expect(validateEmail('userexample.com')).toBe(false);
  });
  it('rejects email missing domain after @', () => {
    expect(validateEmail('user@')).toBe(false);
  });
  it('rejects email missing TLD', () => {
    expect(validateEmail('user@example')).toBe(false);
  });
  it('rejects empty string', () => {
    expect(validateEmail('')).toBe(false);
  });
  it('rejects email with spaces', () => {
    expect(validateEmail('user @example.com')).toBe(false);
  });
});

describe('formatDateGMT', () => {
  it('formats a UTC ISO string correctly', () => {
    expect(formatDateGMT('2026-01-17T05:09:13Z')).toBe('17 Jan 2026');
  });
  it('treats a bare ISO string (no timezone) as UTC', () => {
    expect(formatDateGMT('2026-01-17T05:09:13')).toBe('17 Jan 2026');
  });
  it('handles space-separated datetime without timezone as UTC', () => {
    expect(formatDateGMT('2026-01-17 05:09:13')).toBe('17 Jan 2026');
  });
  it('returns - for null', () => {
    expect(formatDateGMT(null)).toBe('-');
  });
  it('returns - for undefined', () => {
    expect(formatDateGMT(undefined)).toBe('-');
  });
  it('returns - for empty string', () => {
    expect(formatDateGMT('')).toBe('-');
  });
  it('returns - for an invalid date string', () => {
    expect(formatDateGMT('not-a-date')).toBe('-');
  });
});

describe('formatTimeGMT', () => {
  it('returns a time string ending with GMT for a valid date', () => {
    const result = formatTimeGMT('2026-01-17T14:30:45.123Z');
    expect(result).toMatch(/GMT$/);
  });
  it('returns - for null', () => {
    expect(formatTimeGMT(null)).toBe('-');
  });
  it('returns - for an invalid date string', () => {
    expect(formatTimeGMT('bad')).toBe('-');
  });
});

describe('formatDateTimePartsGMT', () => {
  it('returns formatted date and time parts for a valid date', () => {
    const { date, time } = formatDateTimePartsGMT('2026-01-17T14:30:00Z');
    expect(date).toBe('17 Jan 2026');
    expect(time).toMatch(/GMT$/);
  });
  it('returns both parts as - for an invalid date', () => {
    expect(formatDateTimePartsGMT('invalid')).toEqual({ date: '-', time: '-' });
  });
  it('returns both parts as - for null', () => {
    expect(formatDateTimePartsGMT(null)).toEqual({ date: '-', time: '-' });
  });
});

describe('formatDateAEST', () => {
  it('formats a UTC date in AEST (UTC+10)', () => {
    // 2026-01-17T00:00:00Z = 2026-01-17T10:00:00 AEST — still the 17th
    expect(formatDateAEST('2026-01-17T00:00:00Z')).toBe('17 Jan 2026');
  });
  it('rolls over to the next day when UTC time crosses midnight in AEST', () => {
    // 2026-01-16T14:01:00Z = 2026-01-17T00:01:00 AEST
    expect(formatDateAEST('2026-01-16T14:01:00Z')).toBe('17 Jan 2026');
  });
  it('stays on the previous day when UTC is just before AEST midnight', () => {
    // 2026-01-16T13:59:00Z = 2026-01-16T23:59:00 AEST
    expect(formatDateAEST('2026-01-16T13:59:00Z')).toBe('16 Jan 2026');
  });
  it('returns - for null', () => {
    expect(formatDateAEST(null)).toBe('-');
  });
  it('returns - for an invalid date string', () => {
    expect(formatDateAEST('bad')).toBe('-');
  });
});

describe('formatTimeAEST', () => {
  it('returns a time string ending with AEST for a valid date', () => {
    const result = formatTimeAEST('2026-01-17T00:00:00Z');
    expect(result).toMatch(/AEST$/);
  });
  it('returns - for null', () => {
    expect(formatTimeAEST(null)).toBe('-');
  });
  it('returns - for an invalid date string', () => {
    expect(formatTimeAEST('bad')).toBe('-');
  });
});

describe('formatDateTimePartsAEST', () => {
  it('returns formatted date and time parts for a valid date', () => {
    const { date, time } = formatDateTimePartsAEST('2026-01-17T00:00:00Z');
    expect(date).toBe('17 Jan 2026');
    expect(time).toMatch(/AEST$/);
  });
  it('returns both parts as - for an invalid date', () => {
    expect(formatDateTimePartsAEST('invalid')).toEqual({ date: '-', time: '-' });
  });
});

describe('truncateString', () => {
  it('returns the string unchanged if shorter than maxLength', () => {
    expect(truncateString('hello', 10)).toBe('hello');
  });
  it('returns the string unchanged if equal to maxLength', () => {
    expect(truncateString('hello', 5)).toBe('hello');
  });
  it('truncates and appends ellipsis if longer than maxLength', () => {
    expect(truncateString('hello world', 5)).toBe('hello...');
  });
  it('truncates to exactly maxLength characters before the ellipsis', () => {
    expect(truncateString('abcdef', 3)).toBe('abc...');
  });
});
