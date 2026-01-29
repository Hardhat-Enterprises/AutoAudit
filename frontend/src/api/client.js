const API_BASE_URL = import.meta.env.VITE_API_URL;

if (!API_BASE_URL) {
  throw new Error('VITE_API_URL environment variable must be set');
}

export class APIError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "APIError";
    this.status = status;
    this.payload = payload;
  }
}

// Helper for making authenticated requests
async function fetchWithAuth(endpoint, token, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new APIError(error.detail || 'Request failed', response.status, error);
    }

    return response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(error?.message || 'Network error', 0);
  }
}

// Auth endpoints
export async function login(email, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new APIError(error.detail || 'Invalid credentials', response.status, error);
    }

    return response.json();
  } catch (error) {
    throw error;
  }
}

export async function register(email, password) {
  return fetchWithAuth('/v1/auth/register', null, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(token) {
  // Backend uses FastAPI Users; JWT logout typically returns 204 No Content.
  // This is best-effort because JWTs are stateless; the client must clear local auth.
  if (!token) return;

  const response = await fetch(`${API_BASE_URL}/v1/auth/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new APIError(error.detail || 'Logout failed', response.status, error);
  }

  // 204 No Content (common for logout); nothing to parse.
  if (response.status === 204) return;

  // If the backend ever returns JSON, tolerate empty bodies.
  return response.json().catch(() => null);
}

export async function getCurrentUser(token) {
  return fetchWithAuth('/v1/auth/users/me', token);
}

// Contact submissions
export async function createContactSubmission(payload) {
  return fetchWithAuth('/v1/contact', null, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactSubmissions(token) {
  return fetchWithAuth('/v1/contact/submissions', token);
}

export async function getContactSubmission(token, id) {
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token);
}

export async function updateContactSubmission(token, id, payload) {
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteContactSubmission(token, id) {
  const response = await fetch(`${API_BASE_URL}/v1/contact/submissions/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new APIError(error.detail || 'Failed to delete submission', response.status, error);
  }
}

export async function getContactNotes(token, id) {
  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token);
}

export async function addContactNote(token, id, payload) {
  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactHistory(token, id) {
  return fetchWithAuth(`/v1/contact/submissions/${id}/history`, token);
}

// Settings endpoints
export async function getSettings(token) {
  return fetchWithAuth('/v1/settings', token);
}

export async function updateSettings(token, data) {
  return fetchWithAuth('/v1/settings', token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Contact submissions
export async function createContactSubmission(payload) {
  return fetchWithAuth('/v1/contact', null, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactSubmissions(token) {
  return fetchWithAuth('/v1/contact/submissions', token);
}

export async function getContactSubmission(token, id) {
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token);
}

export async function updateContactSubmission(token, id, payload) {
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteContactSubmission(token, id) {
  const response = await fetch(`${API_BASE_URL}/v1/contact/submissions/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new APIError(error.detail || 'Failed to delete submission', response.status, error);
  }
}

export async function getContactNotes(token, id) {
  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token);
}

export async function addContactNote(token, id, payload) {
  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactHistory(token, id) {
  return fetchWithAuth(`/v1/contact/submissions/${id}/history`, token);
}

// Platform endpoints
export async function getPlatforms(token) {
  return fetchWithAuth('/v1/platforms', token);
}

// M365 Connection endpoints
export async function getConnections(token) {
  return fetchWithAuth('/v1/m365-connections/', token);
}

export async function createConnection(token, data) {
  return fetchWithAuth('/v1/m365-connections/', token, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateConnection(token, id, data) {
  return fetchWithAuth(`/v1/m365-connections/${id}`, token, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteConnection(token, id) {
  const response = await fetch(`${API_BASE_URL}/v1/m365-connections/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Failed to delete connection');
  }

  // DELETE returns 204 No Content, so don't try to parse JSON
  return;
}

export async function testConnection(token, id) {
  return fetchWithAuth(`/v1/m365-connections/${id}/test`, token, {
    method: 'POST',
  });
}

// Benchmark endpoints
export async function getBenchmarks(token) {
  return fetchWithAuth('/v1/benchmarks', token);
}

// Scan endpoints
export async function getScans(token) {
  return fetchWithAuth('/v1/scans/', token);
}

export async function getScan(token, id) {
  return fetchWithAuth(`/v1/scans/${id}`, token);
}

export async function createScan(token, data) {
  return fetchWithAuth('/v1/scans/', token, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteScan(token, id) {
  const response = await fetch(`${API_BASE_URL}/v1/scans/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Failed to delete scan');
  }

  // DELETE returns 204 No Content, so don't try to parse JSON
  return;
}

// Evidence scanner endpoints
export async function getEvidenceStrategies() {
  // Frontend -> Backend
  // GET /v1/evidence/strategies
  //
  // Returns an array of strategy objects, e.g.
  // [{ name, description, category, severity, evidence_types }, ...]
  // (see backend-api/app/api/v1/evidence.py -> strategies()).
  return fetchWithAuth('/v1/evidence/strategies', null);
}

export async function scanEvidence(token, { strategyName, file }) {
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

  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
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
      const error = raw ? JSON.parse(raw) : { detail: response.statusText };
      throw new APIError(error.detail || 'Scan failed', response.status, error);
    } catch {
      throw new APIError(raw || 'Scan failed', response.status);
    }
  }

  return response.json();
}

export function getEvidenceReportUrl(filename) {
  // Frontend helper to build a direct download URL for a generated report.
  // Backend endpoint: GET /v1/evidence/reports/{filename}
  if (!filename) return '';
  return `${API_BASE_URL}/v1/evidence/reports/${encodeURIComponent(filename)}`;
}
