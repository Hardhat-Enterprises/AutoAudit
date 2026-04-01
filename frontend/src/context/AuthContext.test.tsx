import React from 'react';
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './AuthContext';

// Mocking api/client prevents client.ts from loading (which would throw without VITE_API_URL)
// and gives us control over login/getCurrentUser responses.
vi.mock('../api/client', () => ({
  login: vi.fn(),
  getCurrentUser: vi.fn(),
  APIError: class APIError extends Error {
    status: number;
    constructor(message: string, status: number) {
      super(message);
      this.name = 'APIError';
      this.status = status;
    }
  },
}));

import { login as mockApiLogin, getCurrentUser as mockGetCurrentUser } from '../api/client';

// Displays context values so tests can assert on them.
function AuthConsumer() {
  const auth = useAuth();
  const [actionError, setActionError] = React.useState('');

  const handleLogin = async () => {
    try {
      await auth.login('user@test.com', 'password');
    } catch (e) {
      setActionError((e as Error).message);
    }
  };

  const handleLoginWithToken = async (token: string) => {
    try {
      await auth.loginWithAccessToken(token);
    } catch (e) {
      setActionError((e as Error).message);
    }
  };

  return (
    <div>
      <span data-testid="authenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="loading">{String(auth.isLoading)}</span>
      <span data-testid="token">{auth.token ?? 'null'}</span>
      <span data-testid="user-email">{auth.user?.email ?? 'null'}</span>
      {actionError && <span data-testid="action-error">{actionError}</span>}
      <button onClick={() => auth.logout()}>Logout</button>
      <button onClick={handleLogin}>Login</button>
      <button onClick={() => handleLoginWithToken('my-access-token')}>LoginWithToken</button>
      <button onClick={() => handleLoginWithToken('')}>LoginWithEmptyToken</button>
    </div>
  );
}

function renderWithProvider() {
  return render(
    <AuthProvider>
      <AuthConsumer />
    </AuthProvider>
  );
}

function waitForLoaded() {
  return waitFor(() =>
    expect(screen.getByTestId('loading')).toHaveTextContent('false')
  );
}

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  vi.clearAllMocks();
  // Default: getCurrentUser resolves so token validation succeeds
  vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 1, email: 'user@test.com' });
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
});

// --- useAuth guard ---

describe('useAuth', () => {
  test('throws when used outside an AuthProvider', () => {
    function Consumer() {
      useAuth();
      return null;
    }
    expect(() => render(<Consumer />)).toThrow(/useAuth must be used within an AuthProvider/i);
  });
});

// --- Initial state ---

describe('AuthProvider initial state', () => {
  test('isAuthenticated is false when no credentials are stored', async () => {
    renderWithProvider();
    await waitForLoaded();
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  test('isLoading becomes false after startup validation', async () => {
    renderWithProvider();
    await waitForLoaded();
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
  });

  test('loads token and user from localStorage on mount', async () => {
    localStorage.setItem('token', 'stored-token');
    localStorage.setItem('user', JSON.stringify({ email: 'stored@test.com' }));
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ email: 'stored@test.com' });

    renderWithProvider();
    await waitForLoaded();

    expect(screen.getByTestId('token')).toHaveTextContent('stored-token');
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
  });

  test('falls back to sessionStorage when localStorage has no token', async () => {
    sessionStorage.setItem('token', 'session-token');
    sessionStorage.setItem('user', JSON.stringify({ email: 'session@test.com' }));
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ email: 'session@test.com' });

    renderWithProvider();
    await waitForLoaded();

    expect(screen.getByTestId('token')).toHaveTextContent('session-token');
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
  });
});

// --- Token validation on mount ---

describe('AuthProvider token validation', () => {
  test('clears auth when the stored token returns a 401', async () => {
    localStorage.setItem('token', 'expired-token');
    localStorage.setItem('user', JSON.stringify({ email: 'u@test.com' }));

    // Import the mock APIError class to construct a proper 401 instance
    const { APIError: MockAPIError } = await import('../api/client');
    vi.mocked(mockGetCurrentUser).mockRejectedValue(
      new (MockAPIError as new (msg: string, status: number) => Error)('Unauthorized', 401)
    );

    renderWithProvider();
    await waitForLoaded();

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(localStorage.getItem('token')).toBeNull();
  });
});

// --- logout ---

describe('AuthProvider logout', () => {
  test('sets isAuthenticated to false', async () => {
    localStorage.setItem('token', 'tok');
    localStorage.setItem('user', JSON.stringify({ email: 'u@test.com' }));

    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'Logout' }));

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  test('removes token and user from both localStorage and sessionStorage', async () => {
    localStorage.setItem('token', 'tok');
    localStorage.setItem('user', JSON.stringify({ email: 'u@test.com' }));
    sessionStorage.setItem('token', 'session-tok');
    sessionStorage.setItem('user', JSON.stringify({ email: 'u@test.com' }));

    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'Logout' }));

    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
    expect(sessionStorage.getItem('token')).toBeNull();
    expect(sessionStorage.getItem('user')).toBeNull();
  });
});

// --- login ---

describe('AuthProvider login', () => {
  beforeEach(() => {
    vi.mocked(mockApiLogin).mockResolvedValue({ access_token: 'new-token' });
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 1, email: 'user@test.com' });
  });

  test('calls apiLogin with the provided email and password', async () => {
    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'Login' }));

    expect(mockApiLogin).toHaveBeenCalledWith('user@test.com', 'password');
  });

  test('calls getCurrentUser with the access token from the login response', async () => {
    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'Login' }));

    await waitFor(() =>
      expect(mockGetCurrentUser).toHaveBeenCalledWith('new-token')
    );
  });

  test('persists the token to localStorage by default (remember = true)', async () => {
    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'Login' }));

    await waitFor(() =>
      expect(localStorage.getItem('token')).toBe('new-token')
    );
  });

  test('sets isAuthenticated to true after a successful login', async () => {
    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'Login' }));

    await waitFor(() =>
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    );
  });
});

// --- loginWithAccessToken ---

describe('AuthProvider loginWithAccessToken', () => {
  test('throws when an empty access token is provided', async () => {
    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'LoginWithEmptyToken' }));

    await waitFor(() =>
      expect(screen.getByTestId('action-error')).toHaveTextContent('Access token is required')
    );
  });

  test('calls getCurrentUser with the provided access token', async () => {
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 2, email: 'oauth@test.com' });

    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'LoginWithToken' }));

    await waitFor(() =>
      expect(mockGetCurrentUser).toHaveBeenCalledWith('my-access-token')
    );
  });

  test('persists token to sessionStorage by default (remember = false)', async () => {
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 2, email: 'oauth@test.com' });

    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'LoginWithToken' }));

    await waitFor(() =>
      expect(sessionStorage.getItem('token')).toBe('my-access-token')
    );
  });

  test('sets isAuthenticated to true after a successful loginWithAccessToken', async () => {
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 2, email: 'oauth@test.com' });

    renderWithProvider();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: 'LoginWithToken' }));

    await waitFor(() =>
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    );
  });
});
