import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AccountPage from './AccountPage';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual<typeof import('react-router-dom')>('react-router-dom')),
  useNavigate: () => mockNavigate,
}));

vi.mock('../api/client', () => ({
  logout: vi.fn(),
}));

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

import { logout as mockApiLogout } from '../api/client';
import { useAuth as mockUseAuth } from '../context/AuthContext';

function setupAuth(user: Record<string, unknown> | null, token = 'test-token') {
  vi.mocked(mockUseAuth).mockReturnValue({
    user,
    token,
    logout: vi.fn(),
  } as ReturnType<typeof mockUseAuth>);
}

function renderPage() {
  return render(<AccountPage />);
}

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// --- primaryLabel fallback chain ---

describe('primaryLabel', () => {
  it('displays email when present', () => {
    setupAuth({ email: 'user@example.com', username: 'u', name: 'Name', id: 1 });
    renderPage();
    expect(screen.getByText('user@example.com')).toBeInTheDocument();
  });

  it('falls back to username when email is absent', () => {
    setupAuth({ email: null, username: 'jdoe', name: 'John', id: 2 });
    renderPage();
    expect(screen.getByText('jdoe')).toBeInTheDocument();
  });

  it('falls back to name when email and username are absent', () => {
    setupAuth({ email: null, username: null, name: 'John Doe', id: 3 });
    renderPage();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('falls back to id as string when email, username, and name are absent', () => {
    setupAuth({ email: null, username: null, name: null, id: 99 });
    renderPage();
    expect(screen.getByText('99')).toBeInTheDocument();
  });

  it('shows "Signed in" when user is null', () => {
    setupAuth(null);
    renderPage();
    expect(screen.getByText('Signed in')).toBeInTheDocument();
  });

  it('shows "Signed in" when all user fields are null or undefined', () => {
    setupAuth({ email: null, username: null, name: null, id: null });
    renderPage();
    expect(screen.getByText('Signed in')).toBeInTheDocument();
  });
});

// --- handleLogout ---

describe('handleLogout', () => {
  it('calls apiLogout with the current token', async () => {
    setupAuth({ email: 'u@test.com' }, 'my-token');
    vi.mocked(mockApiLogout).mockResolvedValue(undefined);

    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /log out/i }));

    expect(mockApiLogout).toHaveBeenCalledWith('my-token');
  });

  it('calls clearAuth and navigates to / after successful logout', async () => {
    const clearAuth = vi.fn();
    vi.mocked(mockUseAuth).mockReturnValue({
      user: { email: 'u@test.com' },
      token: 'tok',
      logout: clearAuth,
    } as ReturnType<typeof mockUseAuth>);
    vi.mocked(mockApiLogout).mockResolvedValue(undefined);

    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /log out/i }));

    await waitFor(() => {
      expect(clearAuth).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('still clears auth and navigates when apiLogout fails (best-effort)', async () => {
    const clearAuth = vi.fn();
    vi.mocked(mockUseAuth).mockReturnValue({
      user: { email: 'u@test.com' },
      token: 'tok',
      logout: clearAuth,
    } as ReturnType<typeof mockUseAuth>);
    vi.mocked(mockApiLogout).mockRejectedValue(new Error('Network error'));

    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /log out/i }));

    await waitFor(() => {
      expect(clearAuth).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });
});
