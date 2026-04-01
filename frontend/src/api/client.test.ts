import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  APIError,
  getEvidenceReportUrl,
  scanEvidence,
  login,
  getCurrentUser,
  getSettings,
} from './client';

// Builds a minimal fetch Response mock for a given status and body.
function mockResponse(status: number, body?: unknown): Response {
  const ok = status >= 200 && status < 300;
  return {
    ok,
    status,
    statusText: ok ? 'OK' : 'Error',
    json: vi.fn().mockResolvedValue(body ?? {}),
    text: vi.fn().mockResolvedValue(JSON.stringify(body ?? {})),
  } as unknown as Response;
}

// --- APIError ---

describe('APIError', () => {
  it('has name APIError', () => {
    expect(new APIError('msg', 400).name).toBe('APIError');
  });

  it('is an instance of Error', () => {
    expect(new APIError('msg', 500)).toBeInstanceOf(Error);
  });

  it('stores status', () => {
    expect(new APIError('msg', 422).status).toBe(422);
  });

  it('stores payload when provided', () => {
    const payload = { detail: 'Validation failed' };
    expect(new APIError('msg', 422, payload).payload).toEqual(payload);
  });

  it('payload is undefined when not provided', () => {
    expect(new APIError('msg', 404).payload).toBeUndefined();
  });
});

// --- getEvidenceReportUrl ---

describe('getEvidenceReportUrl', () => {
  it('returns empty string for an empty filename', () => {
    expect(getEvidenceReportUrl('')).toBe('');
  });

  it('builds the correct URL for a plain filename', () => {
    expect(getEvidenceReportUrl('report.pdf')).toBe(
      'http://localhost:8000/v1/evidence/reports/report.pdf'
    );
  });

  it('URL-encodes special characters in the filename', () => {
    expect(getEvidenceReportUrl('my report (1).pdf')).toBe(
      'http://localhost:8000/v1/evidence/reports/my%20report%20(1).pdf'
    );
  });
});

// --- scanEvidence input validation ---

describe('scanEvidence', () => {
  it('throws when strategyName is empty', async () => {
    await expect(
      scanEvidence('token', { strategyName: '', file: new Blob(['data']) })
    ).rejects.toThrow('Strategy is required');
  });

  it('throws when file is falsy', async () => {
    await expect(
      scanEvidence('token', { strategyName: 'my-strategy', file: null as unknown as File })
    ).rejects.toThrow('Evidence file is required');
  });
});

// --- login ---

describe('login', () => {
  beforeEach(() => vi.stubGlobal('fetch', vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it('calls fetch with POST and form-urlencoded content type', async () => {
    vi.mocked(fetch).mockResolvedValue(
      mockResponse(200, { access_token: 'tok' })
    );

    await login('user@example.com', 'pass');

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/x-www-form-urlencoded',
        }),
      })
    );
  });

  it('sends email as username and password in the body', async () => {
    vi.mocked(fetch).mockResolvedValue(
      mockResponse(200, { access_token: 'tok' })
    );

    await login('user@example.com', 'mypassword');

    const body = new URLSearchParams(
      (vi.mocked(fetch).mock.calls[0][1] as RequestInit).body as string
    );
    expect(body.get('username')).toBe('user@example.com');
    expect(body.get('password')).toBe('mypassword');
  });

  it('returns parsed response data on success', async () => {
    vi.mocked(fetch).mockResolvedValue(
      mockResponse(200, { access_token: 'abc', token_type: 'bearer' })
    );

    const result = await login('a@b.com', 'pass');
    expect(result.access_token).toBe('abc');
  });

  it('throws APIError on a non-ok response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(401, { detail: 'Invalid credentials' }));
    await expect(login('a@b.com', 'wrong')).rejects.toBeInstanceOf(APIError);
  });

  it('throws APIError with the detail message from the response body', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(401, { detail: 'Bad credentials' }));
    await expect(login('a@b.com', 'wrong')).rejects.toThrow('Bad credentials');
  });
});

// --- fetchWithAuth (tested via getCurrentUser) ---

describe('fetchWithAuth via getCurrentUser', () => {
  beforeEach(() => vi.stubGlobal('fetch', vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it('includes Authorization Bearer header when a token is provided', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, { id: 1, email: 'u@test.com' }));

    await getCurrentUser('my-token');

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/v1/auth/users/me'),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer my-token' }),
      })
    );
  });

  it('omits Authorization header when token is null', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(200, { id: 1 }));

    await getCurrentUser(null);

    const headers = (vi.mocked(fetch).mock.calls[0][1] as RequestInit)
      .headers as Record<string, string>;
    expect(headers.Authorization).toBeUndefined();
  });

  it('throws APIError with the detail message on a non-ok response', async () => {
    vi.mocked(fetch).mockResolvedValue(mockResponse(401, { detail: 'Unauthorized' }));
    await expect(getCurrentUser('bad-token')).rejects.toThrow('Unauthorized');
  });

  it('throws APIError with status 0 on a network failure', async () => {
    vi.mocked(fetch).mockRejectedValue(new Error('Network error'));

    const err = await getCurrentUser('token').catch((e) => e);
    expect(err).toBeInstanceOf(APIError);
    expect(err.status).toBe(0);
  });
});

// --- fetchWithAuth 204 handling (tested via getSettings) ---

describe('fetchWithAuth 204 No Content handling', () => {
  beforeEach(() => vi.stubGlobal('fetch', vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it('returns undefined for a 204 No Content response', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 204,
      json: vi.fn(),
      text: vi.fn(),
    } as unknown as Response);

    const result = await getSettings('token');
    expect(result).toBeUndefined();
  });
});
