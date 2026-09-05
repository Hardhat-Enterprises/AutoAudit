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
  } as unknown as ReturnType<typeof mockUseAuth>);
}

function renderPage() {
  return render(<AccountPage />);
}

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// --- primaryLabel fallback chain ---

describe('account details fallbacks', () => {
  it('displays name, email, and organization when present', () => {
    setupAuth({
      email: 'user@example.com',
      first_name: 'Jane',
      last_name: 'Doe',
      organization_name: 'Acme Inc',
    });
    renderPage();
    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('user@example.com')).toBeInTheDocument();
    expect(screen.getByText('Acme Inc')).toBeInTheDocument();
  });

  it('shows "Not available" for name when only one of first_name/last_name is present', () => {
    setupAuth({ email: 'user@example.com', first_name: 'Jane', last_name: null });
    renderPage();
    expect(screen.getAllByText('Not available')).toHaveLength(2); // name + organization
  });

  it('shows "Not available" for email when absent', () => {
    setupAuth({ email: null, first_name: 'Jane', last_name: 'Doe' });
    renderPage();
    expect(screen.getAllByText('Not available')).toHaveLength(2); // email + organization
  });

  it('shows "Not available" for all fields when user is null', () => {
    setupAuth(null);
    renderPage();
    expect(screen.getAllByText('Not available')).toHaveLength(3);
  });
});

// --- handleLogout ---

describe('handleLogout', () => {
  it('does not call the raw api client directly (avoids duplicate logout requests)', async () => {
  setupAuth({ email: 'u@test.com' }, 'my-token');

  renderPage();
  await userEvent.click(screen.getByRole('button', { name: /log out/i }));

  expect(mockApiLogout).not.toHaveBeenCalled();
});

  it('calls clearAuth and navigates to / after successful logout', async () => {
    const clearAuth = vi.fn();
    vi.mocked(mockUseAuth).mockReturnValue({
      user: { email: 'u@test.com' },
      token: 'tok',
      logout: clearAuth,
    } as unknown as ReturnType<typeof mockUseAuth>);
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
    } as unknown as ReturnType<typeof mockUseAuth>);
    vi.mocked(mockApiLogout).mockRejectedValue(new Error('Network error'));

    renderPage();
    await userEvent.click(screen.getByRole('button', { name: /log out/i }));

    await waitFor(() => {
      expect(clearAuth).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });
});
