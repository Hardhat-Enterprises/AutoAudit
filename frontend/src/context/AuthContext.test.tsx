import React from 'react';
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './AuthContext';

// Mocking api/client prevents client.ts from loading (which would throw without VITE_API_URL)
// and gives us control over login/logout/getCurrentUser responses.
vi.mock('../api/client', () => ({
  login: vi.fn(),
  logout: vi.fn(),
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

import {
  login as mockApiLogin,
  logout as mockApiLogout,
  getCurrentUser as mockGetCurrentUser,
} from '../api/client';

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

  const handleCompleteOAuthLogin = async () => {
    try {
      await auth.completeOAuthLogin();
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
      <button onClick={handleCompleteOAuthLogin}>CompleteOAuthLogin</button>
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

beforeEach(async () => {
  sessionStorage.clear();
  vi.clearAllMocks();
  // Default: no session cookie present, so the /users/me check on mount
  // comes back 401. Individual tests override this to simulate a live session.
  const { APIError: MockAPIError } = await import('../api/client');
  vi.mocked(mockGetCurrentUser).mockRejectedValue(
    new (MockAPIError as new (msg: string, status: number) => Error)('Unauthorized', 401)
  );
});

afterEach(() => {
  cleanup();
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
  test('isAuthenticated is false when no session cookie is present', async () => {
    renderWithProvider();
    await waitForLoaded();
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  test('isLoading becomes false after startup validation', async () => {
    renderWithProvider();
    await waitForLoaded();
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
  });

  test('token is always null (session lives in an HttpOnly cookie, not readable by JS)', async () => {
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ email: 'user@test.com' });
    renderWithProvider();
    await waitForLoaded();
    expect(screen.getByTestId('token')).toHaveTextContent('null');
  });

  test('seeds the user from the sessionStorage cache immediately, before /users/me resolves', () => {
    sessionStorage.setItem('user', JSON.stringify({ email: 'cached@test.com' }));
    vi.mocked(mockGetCurrentUser).mockReturnValue(new Promise(() => {})); // never resolves in this test
    renderWithProvider();
    expect(screen.getByTestId('user-email')).toHaveTextContent('cached@test.com');
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
  });

  test('replaces the cached user with the confirmed /users/me result once validation resolves', async () => {
    sessionStorage.setItem('user', JSON.stringify({ email: 'stale@test.com' }));
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ email: 'fresh@test.com' });
    renderWithProvider();
    await waitForLoaded();
    expect(screen.getByTestId('user-email')).toHaveTextContent('fresh@test.com');
  });
});

// --- Session validation on mount ---

describe('AuthProvider session validation', () => {
  test('calls getCurrentUser with null (auth comes from the cookie, not a JS-held token)', async () => {
    renderWithProvider();
    await waitForLoaded();
    expect(mockGetCurrentUser).toHaveBeenCalledWith(null);
  });

  test('clears auth and the cache when the session check returns a 401', async () => {
    sessionStorage.setItem('user', JSON.stringify({ email: 'u@test.com' }));
    // beforeEach already made getCurrentUser reject with a 401.
    renderWithProvider();
    await waitForLoaded();
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(sessionStorage.getItem('user')).toBeNull();
  });
});

// --- login ---

describe('AuthProvider login', () => {
  beforeEach(() => {
    vi.mocked(mockApiLogin).mockResolvedValue(undefined);
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 1, email: 'user@test.com' });
  });

  test('calls apiLogin with the provided email and password', async () => {
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'Login' }));
    expect(mockApiLogin).toHaveBeenCalledWith('user@test.com', 'password');
  });

  test('confirms the session via getCurrentUser(null) after login (no token to pass)', async () => {
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'Login' }));
    await waitFor(() => expect(mockGetCurrentUser).toHaveBeenLastCalledWith(null));
  });

  test('sets isAuthenticated to true and caches the user after a successful login', async () => {
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'Login' }));
    await waitFor(() =>
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    );
    expect(sessionStorage.getItem('user')).toContain('user@test.com');
  });

  test('surfaces an error from apiLogin without crashing', async () => {
    vi.mocked(mockApiLogin).mockRejectedValue(new Error('Invalid credentials'));
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'Login' }));
    await waitFor(() =>
      expect(screen.getByTestId('action-error')).toHaveTextContent('Invalid credentials')
    );
  });
});

// --- completeOAuthLogin ---

describe('AuthProvider completeOAuthLogin', () => {
  test('confirms the session via getCurrentUser(null) without calling apiLogin', async () => {
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 2, email: 'oauth@test.com' });
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'CompleteOAuthLogin' }));
    await waitFor(() =>
      expect(screen.getByTestId('user-email')).toHaveTextContent('oauth@test.com')
    );
    expect(mockApiLogin).not.toHaveBeenCalled();
  });

  test('sets isAuthenticated to true after a successful completeOAuthLogin', async () => {
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ id: 2, email: 'oauth@test.com' });
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'CompleteOAuthLogin' }));
    await waitFor(() =>
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    );
  });

  test('surfaces an error when the session cannot be confirmed', async () => {
  renderWithProvider();
  await waitForLoaded();
  // Set the one-time rejection only now, so it's consumed by the click below,
  // not by the mount-time validateSession() call.
  vi.mocked(mockGetCurrentUser).mockRejectedValueOnce(new Error('Session confirmation failed'));
  await userEvent.click(screen.getByRole('button', { name: 'CompleteOAuthLogin' }));
  await waitFor(() =>
    expect(screen.getByTestId('action-error')).toHaveTextContent('Session confirmation failed')
    );
  });
});

// --- logout ---

describe('AuthProvider logout', () => {
  beforeEach(() => {
    vi.mocked(mockApiLogout).mockResolvedValue(undefined);
  });

  test('calls apiLogout', async () => {
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'Logout' }));
    await waitFor(() => expect(mockApiLogout).toHaveBeenCalled());
  });

  test('sets isAuthenticated to false and clears the cached user', async () => {
    sessionStorage.setItem('user', JSON.stringify({ email: 'u@test.com' }));
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ email: 'u@test.com' });
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'Logout' }));
    await waitFor(() =>
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    );
    expect(sessionStorage.getItem('user')).toBeNull();
  });

  test('clears local state even if apiLogout rejects with a 401', async () => {
    const { APIError: MockAPIError } = await import('../api/client');
    vi.mocked(mockApiLogout).mockRejectedValue(
      new (MockAPIError as new (msg: string, status: number) => Error)('Unauthorized', 401)
    );
    sessionStorage.setItem('user', JSON.stringify({ email: 'u@test.com' }));
    vi.mocked(mockGetCurrentUser).mockResolvedValue({ email: 'u@test.com' });
    renderWithProvider();
    await waitForLoaded();
    await userEvent.click(screen.getByRole('button', { name: 'Logout' }));
    await waitFor(() =>
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    );
  });
});