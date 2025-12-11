const API_BASE_URL = process.env.REACT_APP_API_URL;

if (!API_BASE_URL) {
  throw new Error('REACT_APP_API_URL environment variable must be set');
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

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

// Auth endpoints
export async function login(email, password) {
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
    throw new Error(error.detail || 'Invalid credentials');
  }

  return response.json();
}

export async function getCurrentUser(token) {
  return fetchWithAuth('/v1/auth/users/me', token);
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
