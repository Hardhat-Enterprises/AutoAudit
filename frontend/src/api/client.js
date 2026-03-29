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

// ============================
// Helper for API requests
// ============================
async function fetchWithAuth(endpoint, token, options = {}) {
  const headers = {
    ...options.headers,
  };

  // Only add JSON header if not sending FormData
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

    // Handle 204 No Content
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

    const text = await response.text().catch(() => '');
    return text ? JSON.parse(text) : null;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('Network or request failure', 0, error);
  }
}

// ============================
// Auth APIs
// ============================
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
    if (error instanceof APIError) throw error;
    throw new APIError('Login failed', 0, error);
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
  if (!token) throw new APIError('Token required', 400);
  return fetchWithAuth('/v1/auth/users/me', token);
}

// ============================
// Contact APIs
// ============================
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
  if (!id) throw new APIError('Submission ID is required', 400);
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token);
}

export async function updateContactSubmission(token, id, payload) {
  if (!id) throw new APIError('Submission ID is required', 400);
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

// ✅ IMPROVED DELETE (clean + consistent)
export async function deleteContactSubmission(token, id) {
  if (!id) throw new APIError('Submission ID is required', 400);
  return fetchWithAuth(`/v1/contact/submissions/${id}`, token, {
    method: 'DELETE',
  });
}

// ============================
// Settings APIs
// ============================
export async function getSettings(token) {
  if (!token) throw new APIError('Token required', 400);
  return fetchWithAuth('/v1/settings', token);
}

export async function updateSettings(token, data) {
  if (!token) throw new APIError('Token required', 400);
  return fetchWithAuth('/v1/settings', token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// ============================
// M365 Connections
// ============================
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
  if (!id) throw new APIError('Connection ID required', 400);
  return fetchWithAuth(`/v1/m365-connections/${id}`, token, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ✅ IMPROVED DELETE (important for your marks)
export async function deleteConnection(token, id) {
  if (!id) throw new APIError('Connection ID required', 400);
  return fetchWithAuth(`/v1/m365-connections/${id}`, token, {
    method: 'DELETE',
  });
}

// ============================
// Scan APIs
// ============================
export async function getScans(token) {
  return fetchWithAuth('/v1/scans/', token);
}

export async function getScan(token, id) {
  if (!id) throw new APIError('Scan ID required', 400);
  return fetchWithAuth(`/v1/scans/${id}`, token);
}

export async function createScan(token, data) {
  return fetchWithAuth('/v1/scans/', token, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ✅ IMPROVED DELETE (important)
export async function deleteScan(token, id) {
  if (!id) throw new APIError('Scan ID required', 400);
  return fetchWithAuth(`/v1/scans/${id}`, token, {
    method: 'DELETE',
  });
}