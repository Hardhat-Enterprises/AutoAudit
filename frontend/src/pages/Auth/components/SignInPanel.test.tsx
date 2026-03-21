import React from 'react';
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SignInPanel from './SignInPanel';
import { useAuth } from '../../../context/AuthContext';

vi.mock('../../../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

const mockLogin = vi.fn();

function setupAuth() {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    login: mockLogin,
    loginWithAccessToken: vi.fn(),
    logout: vi.fn(),
  });
}

describe('SignInPanel', () => {
  beforeEach(() => {
    setupAuth();
    mockLogin.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  test('renders sign-in form', () => {
    render(<SignInPanel />);
    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^sign in$/i })).toBeInTheDocument();
  });

  test('calls onLogin when provided and credentials are submitted', async () => {
    const onLogin = vi.fn().mockResolvedValue(undefined);
    render(<SignInPanel onLogin={onLogin} onSignUpClick={vi.fn()} />);

    await userEvent.type(screen.getByLabelText(/email address/i), 'user@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'secretpass');
    await userEvent.click(screen.getByRole('button', { name: /^sign in$/i }));

    await waitFor(() => {
      expect(onLogin).toHaveBeenCalledWith('user@example.com', 'secretpass', true);
    });
    expect(mockLogin).not.toHaveBeenCalled();
  });

  test('calls auth.login when onLogin is omitted', async () => {
    mockLogin.mockResolvedValue({ id: 1, email: 'u@x.com' });
    render(<SignInPanel />);

    await userEvent.type(screen.getByLabelText(/email address/i), 'solo@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'pw123456');
    await userEvent.click(screen.getByRole('button', { name: /^sign in$/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('solo@example.com', 'pw123456', true);
    });
  });

  test('shows error message when login fails', async () => {
    const onLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'));
    render(<SignInPanel onLogin={onLogin} />);

    await userEvent.type(screen.getByLabelText(/email address/i), 'bad@example.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'wrong');
    await userEvent.click(screen.getByRole('button', { name: /^sign in$/i }));

    await screen.findByText(/invalid credentials/i);
  });

  test('invokes onSignUpClick when Create one is pressed', async () => {
    const onSignUpClick = vi.fn();
    render(<SignInPanel onSignUpClick={onSignUpClick} />);

    await userEvent.click(screen.getByRole('button', { name: /create one/i }));
    expect(onSignUpClick).toHaveBeenCalledTimes(1);
  });

  test('Google button redirects to authorize URL', async () => {
    const assignSpy = vi.fn();
    const originalLocation = window.location;
    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: {
        ...originalLocation,
        assign: assignSpy,
      },
    });

    render(<SignInPanel />);
    await userEvent.click(screen.getByRole('button', { name: /^google$/i }));

    expect(assignSpy).toHaveBeenCalledWith('https://api.test.local/v1/auth/google/authorize');

    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: originalLocation,
    });
  });
});
