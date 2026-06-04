import { describe, it, expect } from 'vitest';
import { normalizeEvidenceItems, formatEvidenceList, parseApiError } from './api';

// --- Mock response helpers ---
// These objects implement only the subset of the Response interface used by parseApiError.

function mockJsonResponse(data: unknown): Response {
  const jsonFn = async () => data;
  return {
    clone: () => ({ json: jsonFn } as unknown as Response),
    text: async () => JSON.stringify(data),
  } as unknown as Response;
}

function mockFailedJsonResponse(textContent = ''): Response {
  return {
    clone: () => ({
      json: async () => { throw new Error('JSON parse error'); },
    } as unknown as Response),
    text: async () => textContent,
  } as unknown as Response;
}

function mockFullyBrokenResponse(): Response {
  return {
    clone: () => ({
      json: async () => { throw new Error('JSON parse error'); },
    } as unknown as Response),
    text: async (): Promise<string> => { throw new Error('text read error'); },
  } as unknown as Response;
}

// --- normalizeEvidenceItems ---

describe('normalizeEvidenceItems', () => {
  it('returns [] for null', () => {
    expect(normalizeEvidenceItems(null)).toEqual([]);
  });
  it('returns [] for undefined', () => {
    expect(normalizeEvidenceItems(undefined)).toEqual([]);
  });
  it('returns [] for empty string', () => {
    expect(normalizeEvidenceItems('')).toEqual([]);
  });
  it('returns array items trimmed', () => {
    expect(normalizeEvidenceItems(['item1', ' item2 '])).toEqual(['item1', 'item2']);
  });
  it('filters empty and whitespace-only array items', () => {
    expect(normalizeEvidenceItems(['item1', '', '   '])).toEqual(['item1']);
  });
  it('splits a string on newlines', () => {
    expect(normalizeEvidenceItems('item1\nitem2\nitem3')).toEqual(['item1', 'item2', 'item3']);
  });
  it('splits a string on semicolons', () => {
    expect(normalizeEvidenceItems('item1;item2;item3')).toEqual(['item1', 'item2', 'item3']);
  });
  it('splits on mixed newline and semicolon delimiters', () => {
    expect(normalizeEvidenceItems('item1\nitem2;item3')).toEqual(['item1', 'item2', 'item3']);
  });
  it('strips leading dash bullets', () => {
    expect(normalizeEvidenceItems(['- item1'])).toEqual(['item1']);
  });
  it('strips leading asterisk bullets', () => {
    expect(normalizeEvidenceItems(['* item2'])).toEqual(['item2']);
  });
  it('strips leading hash characters', () => {
    expect(normalizeEvidenceItems(['# item3'])).toEqual(['item3']);
  });
  it('strips leading bullet point characters', () => {
    expect(normalizeEvidenceItems(['• item4'])).toEqual(['item4']);
  });
  it('strips leading plus characters', () => {
    expect(normalizeEvidenceItems(['+ item5'])).toEqual(['item5']);
  });
  it('filters items that are empty after stripping bullets', () => {
    expect(normalizeEvidenceItems(['- ', '*', '  '])).toEqual([]);
  });
});

// --- formatEvidenceList ---

describe('formatEvidenceList', () => {
  it('behaves identically to normalizeEvidenceItems', () => {
    expect(formatEvidenceList('item1\nitem2')).toEqual(['item1', 'item2']);
  });
  it('returns [] for null', () => {
    expect(formatEvidenceList(null)).toEqual([]);
  });
});

// --- parseApiError ---

describe('parseApiError', () => {
  it('extracts message from the first item in an errors array', async () => {
    const res = mockJsonResponse({ errors: [{ message: 'First error', code: 'ERR_001' }] });
    const result = await parseApiError(res);
    expect(result.message).toBe('First error');
    expect(result.code).toBe('ERR_001');
  });
  it('falls back to data.detail when errors array is absent', async () => {
    const res = mockJsonResponse({ detail: 'Not found' });
    const result = await parseApiError(res);
    expect(result.message).toBe('Not found');
  });
  it('falls back to data.message when detail is absent', async () => {
    const res = mockJsonResponse({ message: 'Something went wrong' });
    const result = await parseApiError(res);
    expect(result.message).toBe('Something went wrong');
  });
  it('uses the provided fallback when no message fields are present', async () => {
    const res = mockJsonResponse({});
    const result = await parseApiError(res, 'Custom fallback');
    expect(result.message).toBe('Custom fallback');
  });
  it('uses the default fallback when no message and no custom fallback provided', async () => {
    const res = mockJsonResponse({});
    const result = await parseApiError(res);
    expect(result.message).toBe('Request failed');
  });
  it('reads has_errors directly from response data when present', async () => {
    const res = mockJsonResponse({ has_errors: true, errors: [] });
    const result = await parseApiError(res);
    expect(result.hasErrors).toBe(true);
  });
  it('infers has_errors from errors array length when has_errors is absent', async () => {
    const res = mockJsonResponse({ errors: [{ message: 'err' }] });
    const result = await parseApiError(res);
    expect(result.hasErrors).toBe(true);
  });
  it('returns the full errors array', async () => {
    const errors = [{ message: 'e1' }, { message: 'e2' }];
    const res = mockJsonResponse({ errors });
    const result = await parseApiError(res);
    expect(result.errors).toEqual(errors);
  });
  it('falls back to response text when JSON parsing fails', async () => {
    const res = mockFailedJsonResponse('Plain text error');
    const result = await parseApiError(res);
    expect(result.message).toBe('Plain text error');
    expect(result.errors).toEqual([]);
    expect(result.hasErrors).toBe(false);
  });
  it('returns the fallback when both JSON and text parsing fail', async () => {
    const res = mockFullyBrokenResponse();
    const result = await parseApiError(res, 'Default fallback');
    expect(result.message).toBe('Default fallback');
  });
  it('returns code from top-level data.code field', async () => {
    const res = mockJsonResponse({ code: 'TOP_LEVEL_CODE', message: 'msg' });
    const result = await parseApiError(res);
    expect(result.code).toBe('TOP_LEVEL_CODE');
  });
});
