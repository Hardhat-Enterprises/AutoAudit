import React from 'react';
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import GoogleCallbackPage from './GoogleCallbackPage';
import { useAuth } from '../../context/AuthContext';

const CALLBACK_CACHE_KEY = 'autoaudit.oauth.google.callback.params';

vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

const loginWithAccessToken = vi.fn();

function setupUseAuth() {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    loginWithAccessToken,
    logout: vi.fn(),
  });
}

function installLocationMock(parts: { hash?: string; search?: string }) {
  const replaceSpy = vi.fn();
  const mockLoc = {
    pathname: '/auth/google/callback',
    search: parts.search ?? '',
    hash: parts.hash ?? '',
    href: `http://localhost/auth/google/callback${parts.search ?? ''}${parts.hash ?? ''}`,
    replace: replaceSpy,
    assign: vi.fn(),
  };
  Object.defineProperty(window, 'location', {
    configurable: true,
    writable: true,
    value: mockLoc,
  });
  return { replaceSpy };
}

let originalLocation: Location;

describe('GoogleCallbackPage', () => {
  beforeEach(() => {
    originalLocation = window.location;
    sessionStorage.removeItem(CALLBACK_CACHE_KEY);
    loginWithAccessToken.mockReset();
    setupUseAuth();
  });

  afterEach(() => {
    cleanup();
    sessionStorage.removeItem(CALLBACK_CACHE_KEY);
    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: originalLocation,
    });
  });

  function renderCallback() {
    return render(
      <MemoryRouter initialEntries={['/auth/google/callback']}>
        <Routes>
          <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
          <Route path="/login" element={<div>Login stub</div>} />
        </Routes>
      </MemoryRouter>
    );
  }

  test('shows loading state while processing', () => {
    installLocationMock({ hash: '#access_token=will-process' });
    loginWithAccessToken.mockImplementation(() => new Promise(() => {}));
    renderCallback();
    expect(screen.getByText(/please wait while we sign you in/i)).toBeInTheDocument();
  });

  test('shows error when OAuth returns error in hash', async () => {
    installLocationMock({
      hash: '#error=access_denied&error_description=User%20cancelled',
    });
    renderCallback();

    expect(await screen.findByRole('heading', { name: /sign-in failed/i })).toBeInTheDocument();
    expect(screen.getByText(/user cancelled/i)).toBeInTheDocument();
    expect(loginWithAccessToken).not.toHaveBeenCalled();
  });

  test('shows error when token is missing', async () => {
    installLocationMock({ hash: '', search: '' });
    renderCallback();

    expect(await screen.findByText(/missing access token/i)).toBeInTheDocument();
    expect(loginWithAccessToken).not.toHaveBeenCalled();
  });

  test('calls loginWithAccessToken and redirects to dashboard on success', async () => {
    const { replaceSpy } = installLocationMock({ hash: '#access_token=fake-jwt-token' });
    loginWithAccessToken.mockResolvedValue({ id: 1, email: 'u@test.com' });

    renderCallback();

    await waitFor(() => {
      expect(loginWithAccessToken).toHaveBeenCalledWith('fake-jwt-token', false);
    });
    expect(replaceSpy).toHaveBeenCalledWith('/dashboard');
  });

  test('shows error when loginWithAccessToken rejects', async () => {
    installLocationMock({ hash: '#access_token=bad' });
    loginWithAccessToken.mockRejectedValue(new Error('Token invalid'));

    renderCallback();

    expect(await screen.findByText(/token invalid/i)).toBeInTheDocument();
  });

  test('Back to sign in navigates to /login', async () => {
    installLocationMock({ hash: '#error=failed' });
    renderCallback();
    await screen.findByRole('button', { name: /back to sign in/i });
    await userEvent.click(screen.getByRole('button', { name: /back to sign in/i }));
    expect(await screen.findByText(/login stub/i)).toBeInTheDocument();
  });
});
