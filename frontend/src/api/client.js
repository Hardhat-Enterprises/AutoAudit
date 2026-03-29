const API_BASE_URL = import.meta.env.VITE_API_URL;

if (!API_BASE_URL) {
  throw new Error('VITE_API_URL environment variable must be set');
}

export class APIError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.payload = payload;
  }
}

// Helper for making authenticated requests
async function fetchWithAuth(endpoint, token, options = {}) {
  const headers = {
    ...options.headers,
  };

  // Only set JSON content type when body is not FormData
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle empty successful responses like 204 No Content
    if (response.ok && response.status === 204) {
      return null;
    }

    if (!response.ok) {
      const raw = await response.text().catch(() => '');
      let errorPayload = { detail: response.statusText };

      try {
        errorPayload = raw ? JSON.parse(raw) : { detail: response.statusText };
      } catch {
        errorPayload = { detail: raw || response.statusText };
      }

      throw new APIError(
        errorPayload.detail || 'Request failed',
        response.status,
        errorPayload
      );
    }

    // Some successful responses may still return an empty body
    const text = await response.text().catch(() => '');
    return text ? JSON.parse(text) : null;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    throw new APIError(
      'Request failed before receiving a response',
      0,
      error
    );
  }
}

// Authentication endpoints: login, register, logout, and current user details
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

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    throw new APIError('Login request failed', 0, error);
  }
}

export async function register(email, password) {
  return fetchWithAuth('/v1/auth/register', null, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(token) {
  if (!token) return null;

  return fetchWithAuth('/v1/auth/logout', token, {
    method: 'POST',
  });
}

export async function getCurrentUser(token) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/auth/users/me', token);
}

// Contact submission endpoints
export async function createContactSubmission(payload) {
  return fetchWithAuth('/v1/contact', null, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactSubmissions(token) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/contact/submissions', token);
}

export async function getContactSubmission(token, id) {
  if (!id) {
    throw new APIError('Submission ID is required', 400);
  }

  return fetchWithAuth(`/v1/contact/submissions/${id}`, token);
}

export async function updateContactSubmission(token, id, payload) {
  if (!id) {
    throw new APIError('Submission ID is required', 400);
  }

  return fetchWithAuth(`/v1/contact/submissions/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteContactSubmission(token, id) {
  if (!id) {
    throw new APIError('Submission ID is required', 400);
  }

  return fetchWithAuth(`/v1/contact/submissions/${id}`, token, {
    method: 'DELETE',
  });
}

export async function getContactNotes(token, id) {
  if (!id) {
    throw new APIError('Submission ID is required', 400);
  }

  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token);
}

export async function addContactNote(token, id, payload) {
  if (!id) {
    throw new APIError('Submission ID is required', 400);
  }

  return fetchWithAuth(`/v1/contact/submissions/${id}/notes`, token, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getContactHistory(token, id) {
  if (!id) {
    throw new APIError('Submission ID is required', 400);
  }

  return fetchWithAuth(`/v1/contact/submissions/${id}/history`, token);
}

// Settings endpoints
export async function getSettings(token) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/settings', token);
}

export async function updateSettings(token, data) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/settings', token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Platform endpoints
export async function getPlatforms(token) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/platforms', token);
}

// Microsoft 365 connection endpoints
export async function getConnections(token) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/m365-connections/', token);
}

export async function createConnection(token, data) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/m365-connections/', token, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateConnection(token, id, data) {
  if (!id) {
    throw new APIError('Connection ID is required', 400);
  }

  return fetchWithAuth(`/v1/m365-connections/${id}`, token, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteConnection(token, id) {
  if (!id) {
    throw new APIError('Connection ID is required', 400);
  }

  return fetchWithAuth(`/v1/m365-connections/${id}`, token, {
    method: 'DELETE',
  });
}

export async function testConnection(token, id) {
  if (!id) {
    throw new APIError('Connection ID is required', 400);
  }

  return fetchWithAuth(`/v1/m365-connections/${id}/test`, token, {
    method: 'POST',
  });
}

// Benchmark endpoints
export async function getBenchmarks(token) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/benchmarks', token);
}

// Scan endpoints
export async function getScans(token) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/scans/', token);
}

export async function getScan(token, id) {
  if (!id) {
    throw new APIError('Scan ID is required', 400);
  }

  return fetchWithAuth(`/v1/scans/${id}`, token);
}

export async function createScan(token, data) {
  if (!token) {
    throw new APIError('Authentication token is required', 400);
  }

  return fetchWithAuth('/v1/scans/', token, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteScan(token, id) {
  if (!id) {
    throw new APIError('Scan ID is required', 400);
  }

  return fetchWithAuth(`/v1/scans/${id}`, token, {
    method: 'DELETE',
  });
}

// Evidence scanner endpoints
export async function getEvidenceStrategies() {
  return fetchWithAuth('/v1/evidence/strategies', null);
}

export async function scanEvidence(token, { strategyName, file }) {
  if (!strategyName) {
    throw new APIError('Strategy is required', 400);
  }

  if (!file) {
    throw new APIError('Evidence file is required', 400);
  }

  // Use FormData for file uploads. Do not manually set Content-Type here.
  const formData = new FormData();
  formData.append('strategy_name', strategyName);
  formData.append('evidence', file);

  return fetchWithAuth('/v1/evidence/scan', token, {
    method: 'POST',
    body: formData,
  });
}

export function getEvidenceReportUrl(filename) {
  if (!filename) return '';
  return `${API_BASE_URL}/v1/evidence/reports/${encodeURIComponent(filename)}`;
}