const API_BASE_URL = import.meta.env.VITE_API_URL as string | undefined;

if (!API_BASE_URL) {
  throw new Error('VITE_API_URL environment variable must be set');
}

type APIErrorPayload = Record<string, unknown> | undefined;
type AuthToken = string | null | undefined;

export class APIError extends Error {
  status: number;
  payload?: APIErrorPayload;

  constructor(message: string, status: number, payload?: APIErrorPayload) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.payload = payload;
  }
}

function getErrorDetail(payload: unknown, fallback: string): string {
  if (
    payload &&
    typeof payload === 'object' &&
    'detail' in payload &&
    typeof (payload as { detail?: unknown }).detail === 'string'
  ) {
    return (payload as { detail: string }).detail;
  }
  return fallback;
}

// Helper for making authenticated requests
async function fetchWithAuth<T = any>(
  endpoint: string,
  token: AuthToken,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string> | undefined) || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = (await response.json().catch(() => ({ detail: response.statusText }))) as Record<
        string,
        unknown
      >;
      throw new APIError(getErrorDetail(error, 'Request failed'), response.status, error);
    }

    // Support endpoints that may return 204 No Content.
    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } catch (error: unknown) {
    if (error instanceof APIError) {
      throw error;
    }
    const message = error instanceof Error ? error.message : 'Network error';
    throw new APIError(message, 0);
  }
}

// Auth endpoints
export async function login(email: string, password: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      username: email,
      password,
    }),
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({ detail: 'Login failed' }))) as Record<
      string,
      unknown
    >;
    throw new APIError(getErrorDetail(error, 'Invalid credentials'), response.status, error);
  }

  return response.json();
}

export async function register(email: string, password: string): Promise<any> {
  return fetchWithAuth('/v1/auth/register', null, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(token: AuthToken): Promise<any> {
  // Backend uses FastAPI Users; JWT logout typically returns 204 No Content.
  // This is best-effort because JWTs are stateless; the client must clear local auth.
  if (!token) return;

  const response = await fetch(`${API_BASE_URL}/v1/auth/logout`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({ detail: response.statusText }))) as Record<
      string,
      unknown
    >;
    throw new APIError(getErrorDetail(error, 'Logout failed'), response.status, error);
  }

  // 204 No Content (common for logout); nothing to parse.
  if (response.status === 204) return;

  // If the backend ever returns JSON, tolerate empty bodies.
  return response.json().catch(() => null);
}

export async function getCurrentUser(token: AuthToken): Promise<any> {
  return fetchWithAuth('/v1/auth/users/me', token);
}

// Contact submissions
export interface ContactSubmissionCreatePayload {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  company?: string | null;
  subject: string;
  message: string;
  source?: string;
}

export async function createContactSubmission(payload: ContactSubmissionCreatePayload): Promise<any> {
  return fetchWithAuth('/v1/contact', null, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactSubmissions(token: AuthToken): Promise<any> {
  return fetchWithAuth('/v1/contact/submissions', token);
}

export async function getContactSubmission(token: AuthToken, id: string | number): Promise<any> {
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token);
}

export async function updateContactSubmission(
  token: AuthToken,
  id: string | number,
  payload: Record<string, unknown>
): Promise<any> {
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteContactSubmission(token: AuthToken, id: string | number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/v1/contact/submissions/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token || ''}`,
    },
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({ detail: response.statusText }))) as Record<
      string,
      unknown
    >;
    throw new APIError(getErrorDetail(error, 'Failed to delete submission'), response.status, error);
  }
}

export async function getContactNotes(token: AuthToken, id: string | number): Promise<any> {
  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token);
}

export async function addContactNote(
  token: AuthToken,
  id: string | number,
  payload: Record<string, unknown>
): Promise<any> {
  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactHistory(token: AuthToken, id: string | number): Promise<any> {
  return fetchWithAuth(`/v1/contact/submissions/${id}/history`, token);
}

// Settings endpoints
export async function getSettings(token: AuthToken): Promise<any> {
  return fetchWithAuth('/v1/settings', token);
}

export async function updateSettings(token: AuthToken, data: Record<string, unknown>): Promise<any> {
  return fetchWithAuth('/v1/settings', token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Platform endpoints
export async function getPlatforms(token: AuthToken): Promise<any> {
  return fetchWithAuth('/v1/platforms', token);
}

// M365 Connection endpoints
export interface CreateConnectionPayload {
  name: string;
  tenant_id: string;
  client_id: string;
  client_secret: string;
}

export interface UpdateConnectionPayload {
  name?: string;
  tenant_id?: string;
  client_id?: string;
  client_secret?: string;
}

export async function getConnections(token: AuthToken): Promise<any> {
  return fetchWithAuth('/v1/m365-connections/', token);
}

export async function createConnection(token: AuthToken, data: CreateConnectionPayload): Promise<any> {
  return fetchWithAuth('/v1/m365-connections/', token, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateConnection(
  token: AuthToken,
  id: string | number,
  data: UpdateConnectionPayload
): Promise<any> {
  return fetchWithAuth(`/v1/m365-connections/${id}`, token, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteConnection(token: AuthToken, id: string | number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/v1/m365-connections/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token || ''}`,
    },
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({ detail: response.statusText }))) as Record<
      string,
      unknown
    >;
    throw new Error(getErrorDetail(error, 'Failed to delete connection'));
  }

  // DELETE returns 204 No Content, so don't try to parse JSON
  return;
}

export async function testConnection(token: AuthToken, id: string | number): Promise<any> {
  return fetchWithAuth(`/v1/m365-connections/${id}/test`, token, {
    method: 'POST',
  });
}

// Benchmark endpoints
export async function getBenchmarks(token: AuthToken): Promise<any> {
  return fetchWithAuth('/v1/benchmarks', token);
}

// Scan endpoints
export interface CreateScanPayload {
  m365_connection_id: number;
  framework: string;
  benchmark: string;
  version: string;
}

export async function getScans(token: AuthToken): Promise<any> {
  return fetchWithAuth('/v1/scans/', token);
}

export async function getScan(token: AuthToken, id: string | number): Promise<any> {
  return fetchWithAuth(`/v1/scans/${id}`, token);
}

export async function createScan(token: AuthToken, data: CreateScanPayload): Promise<any> {
  return fetchWithAuth('/v1/scans/', token, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteScan(token: AuthToken, id: string | number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/v1/scans/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token || ''}`,
    },
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({ detail: response.statusText }))) as Record<
      string,
      unknown
    >;
    throw new Error(getErrorDetail(error, 'Failed to delete scan'));
  }

  // DELETE returns 204 No Content, so don't try to parse JSON
  return;
}

// Evidence scanner endpoints
export async function getEvidenceStrategies(): Promise<any> {
  // Frontend -> Backend
  // GET /v1/evidence/strategies
  //
  // Returns an array of strategy objects, e.g.
  // [{ name, description, category, severity, evidence_types }, ...]
  // (see backend-api/app/api/v1/evidence.py -> strategies()).
  return fetchWithAuth('/v1/evidence/strategies', null);
}

export interface ScanEvidenceParams {
  strategyName: string;
  file: File | Blob;
}

export async function scanEvidence(token: AuthToken, { strategyName, file }: ScanEvidenceParams): Promise<any> {
  // Frontend -> Backend
  // POST /v1/evidence/scan (multipart/form-data)
  //
  // This uploads an evidence file and tells the backend which strategy to run.
  // The user is derived from the Bearer token (server-side), not a client-provided user_id.
  // Backend returns a JSON payload that the UI renders in the Results section.
  if (!strategyName) {
    throw new Error('Strategy is required');
  }
  if (!file) {
    throw new Error('Evidence file is required');
  }

  const formData = new FormData();
  // These field names must match the FastAPI endpoint signature in:
  // backend-api/app/api/v1/evidence.py -> scan(...)
  formData.append('strategy_name', strategyName);
  formData.append('evidence', file);

  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/v1/evidence/scan`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    // The backend may respond with JSON (FastAPI error) or plain text.
    // We parse best-effort and throw APIError so callers can display a message.
    const raw = await response.text().catch(() => '');
    try {
      const error = (raw ? JSON.parse(raw) : { detail: response.statusText }) as Record<string, unknown>;
      throw new APIError(getErrorDetail(error, 'Scan failed'), response.status, error);
    } catch {
      throw new APIError(raw || 'Scan failed', response.status);
    }
  }

  return response.json();
}

export function getEvidenceReportUrl(filename: string): string {
  // Frontend helper to build a direct download URL for a generated report.
  // Backend endpoint: GET /v1/evidence/reports/{filename}
  if (!filename) return '';
  return `${API_BASE_URL}/v1/evidence/reports/${encodeURIComponent(filename)}`;
}