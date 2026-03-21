import React from 'react';
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import ContactAdminPage, {
  type ContactSubmission,
} from './ContactAdminPage';
import { useAuth } from '../../context/AuthContext';
import {
  getContactSubmissions,
  getContactNotes,
  getContactHistory,
} from '../../api/client';

vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

vi.mock('../../api/client', () => ({
  getContactSubmissions: vi.fn(),
  getContactNotes: vi.fn(),
  getContactHistory: vi.fn(),
  updateContactSubmission: vi.fn(),
  addContactNote: vi.fn(),
  deleteContactSubmission: vi.fn(),
}));

const mockAuthAdmin = {
  user: { id: 1, role: 'admin' as const, email: 'admin@example.com' },
  token: 'test-token',
  isAuthenticated: true,
  isLoading: false,
  login: vi.fn(),
  loginWithAccessToken: vi.fn(),
  logout: vi.fn(),
};

const mockAuthNonAdmin = {
  user: { id: 2, role: 'user' as const, email: 'user@example.com' },
  token: 'test-token',
  isAuthenticated: true,
  isLoading: false,
  login: vi.fn(),
  loginWithAccessToken: vi.fn(),
  logout: vi.fn(),
};

const sampleSubmission: ContactSubmission = {
  id: 42,
  first_name: 'Jane',
  last_name: 'Doe',
  subject: 'Need compliance help',
  status: 'new',
  priority: 'medium',
  message: 'We need an audit next quarter.',
  email: 'jane@example.com',
  phone: null,
  company: 'Acme Corp',
};

function setupUseAuth(value: typeof mockAuthAdmin | typeof mockAuthNonAdmin) {
  vi.mocked(useAuth).mockReturnValue(value as ReturnType<typeof useAuth>);
}

describe('ContactAdminPage', () => {
  beforeEach(() => {
    vi.mocked(getContactNotes).mockResolvedValue([]);
    vi.mocked(getContactHistory).mockResolvedValue([]);
  });

  afterEach(() => {
    cleanup();
  });

  test('shows admin access required for non-admin users', () => {
    setupUseAuth(mockAuthNonAdmin);
    render(<ContactAdminPage />);

    expect(screen.getByRole('heading', { name: /admin access required/i })).toBeInTheDocument();
    expect(
      screen.getByText(/you do not have permission to view this page/i)
    ).toBeInTheDocument();
    expect(vi.mocked(getContactSubmissions)).not.toHaveBeenCalled();
  });

  test('admin sees page title and empty state when there are no submissions', async () => {
    setupUseAuth(mockAuthAdmin);
    vi.mocked(getContactSubmissions).mockResolvedValue([]);

    render(<ContactAdminPage />);

    expect(screen.getByRole('heading', { name: /contact submissions/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/no submissions yet/i)).toBeInTheDocument();
    });

    expect(getContactSubmissions).toHaveBeenCalledWith('test-token');
  });

  test('admin sees submission list and detail after load', async () => {
    setupUseAuth(mockAuthAdmin);
    vi.mocked(getContactSubmissions).mockResolvedValue([sampleSubmission]);

    render(<ContactAdminPage />);

    await screen.findByRole('heading', { name: /jane doe/i });

    expect(
      screen.getByRole('heading', { level: 2, name: /need compliance help/i })
    ).toBeInTheDocument();

    expect(vi.mocked(getContactNotes)).toHaveBeenCalledWith('test-token', 42);
    expect(vi.mocked(getContactHistory)).toHaveBeenCalledWith('test-token', 42);
  });

  test('shows error when loading submissions fails', async () => {
    setupUseAuth(mockAuthAdmin);
    vi.mocked(getContactSubmissions).mockRejectedValue(new Error('Network down'));

    render(<ContactAdminPage />);

    await waitFor(() => {
      expect(screen.getByText(/network down/i)).toBeInTheDocument();
    });
  });
});
