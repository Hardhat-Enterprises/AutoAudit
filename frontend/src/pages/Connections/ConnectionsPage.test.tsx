import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ConnectionsPage from './ConnectionsPage';

vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn().mockReturnValue({ token: 'test-token' }),
}));

vi.mock('../../api/client', () => ({
  // Stub class so the component's `err instanceof APIError` check does not crash.
  // The 400-error branch is reached via the fallback `(err as any)?.status === 400` check.
  APIError: class APIError extends Error {},
  getPlatforms: vi.fn(),
  getConnections: vi.fn(),
  createConnection: vi.fn(),
  updateConnection: vi.fn(),
  deleteConnection: vi.fn(),
  testConnection: vi.fn(),
}));

import {
  getPlatforms as mockGetPlatforms,
  getConnections as mockGetConnections,
  testConnection as mockTestConnection,
  updateConnection as mockUpdateConnection,
} from '../../api/client';

const MASK = '************';

function makeConnection(overrides: Record<string, unknown> = {}) {
  return {
    id: 'conn-1',
    name: 'My Connection',
    tenant_id: 'tenant-abc',
    client_id: 'client-xyz',
    ...overrides,
  };
}

function setupDefault() {
  vi.mocked(mockGetPlatforms).mockResolvedValue([
    { id: 'p1', display_name: 'Microsoft 365' },
  ]);
  vi.mocked(mockGetConnections).mockResolvedValue([]);
}

function renderPage() {
  return render(<ConnectionsPage />);
}

function waitForLoaded() {
  return waitFor(() =>
    expect(screen.queryByText(/loading connections/i)).not.toBeInTheDocument()
  );
}

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// --- Loading state ---

describe('ConnectionsPage loading state', () => {
  it('shows a loading indicator while data is being fetched', () => {
    vi.mocked(mockGetPlatforms).mockReturnValue(new Promise(() => {}));
    vi.mocked(mockGetConnections).mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading connections/i)).toBeInTheDocument();
  });
});

// --- Error state ---

describe('ConnectionsPage error state', () => {
  it('shows an error banner when loadData rejects', async () => {
    vi.mocked(mockGetPlatforms).mockRejectedValue(new Error('Network failure'));
    vi.mocked(mockGetConnections).mockResolvedValue([]);
    renderPage();
    await waitFor(() =>
      expect(screen.getByText('Network failure')).toBeInTheDocument()
    );
  });
});

// --- Connections list ---

describe('ConnectionsPage connections list', () => {
  it('renders the empty state when there are no connections', async () => {
    setupDefault();
    renderPage();
    await waitForLoaded();
    expect(screen.getByText(/no connections yet/i)).toBeInTheDocument();
  });

  it('renders a connection by name', async () => {
    vi.mocked(mockGetPlatforms).mockResolvedValue([]);
    vi.mocked(mockGetConnections).mockResolvedValue([makeConnection()]);
    renderPage();
    await waitForLoaded();
    expect(screen.getByText('My Connection')).toBeInTheDocument();
  });
});

// --- getConnectionErrorMessage (tested via testConnection error behaviour) ---

describe('getConnectionErrorMessage', () => {
  it('shows the specific auth message when a 400 error occurs', async () => {
    vi.mocked(mockGetPlatforms).mockResolvedValue([]);
    vi.mocked(mockGetConnections).mockResolvedValue([makeConnection()]);
    // Simulate a 400-status error without needing instanceof APIError
    vi.mocked(mockTestConnection).mockRejectedValue(
      Object.assign(new Error('bad request'), { status: 400 })
    );

    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: /^test$/i }));

    await waitFor(() =>
      expect(
        screen.getByText(/authentication not established/i)
      ).toBeInTheDocument()
    );
  });

  it('shows the error message for non-400 errors', async () => {
    vi.mocked(mockGetPlatforms).mockResolvedValue([]);
    vi.mocked(mockGetConnections).mockResolvedValue([makeConnection()]);
    vi.mocked(mockTestConnection).mockRejectedValue(new Error('Timeout'));

    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: /^test$/i }));

    await waitFor(() =>
      expect(screen.getByText('Timeout')).toBeInTheDocument()
    );
  });
});

// --- startEditing (client_secret masking) ---

describe('startEditing', () => {
  it('populates the client_secret field with the mask when editing begins', async () => {
    vi.mocked(mockGetPlatforms).mockResolvedValue([]);
    vi.mocked(mockGetConnections).mockResolvedValue([makeConnection()]);

    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: /edit/i }));

    expect(screen.getByDisplayValue(MASK)).toBeInTheDocument();
  });
});

// --- handleEditSubmit (client_secret omitted when mask unchanged) ---

describe('handleEditSubmit', () => {
  it('omits client_secret from the update payload when the mask was not changed', async () => {
    vi.mocked(mockGetPlatforms).mockResolvedValue([]);
    vi.mocked(mockGetConnections).mockResolvedValue([makeConnection()]);
    vi.mocked(mockUpdateConnection).mockResolvedValue(makeConnection());

    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: /edit/i }));
    // Submit the edit form without touching the client_secret field
    await userEvent.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => expect(mockUpdateConnection).toHaveBeenCalled());

    const [, , updateData] = vi.mocked(mockUpdateConnection).mock.calls[0];
    expect(updateData).not.toHaveProperty('client_secret');
  });

  it('includes client_secret when the user enters a new value', async () => {
    vi.mocked(mockGetPlatforms).mockResolvedValue([]);
    vi.mocked(mockGetConnections).mockResolvedValue([makeConnection()]);
    vi.mocked(mockUpdateConnection).mockResolvedValue(makeConnection());

    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('button', { name: /edit/i }));

    // Clear the mask and type a new secret
    const secretInput = screen.getByDisplayValue(MASK);
    await userEvent.clear(secretInput);
    await userEvent.type(secretInput, 'new-secret-value');

    await userEvent.click(screen.getByRole('button', { name: /save changes/i }));

    await waitFor(() => expect(mockUpdateConnection).toHaveBeenCalled());

    const [, , updateData] = vi.mocked(mockUpdateConnection).mock.calls[0];
    expect(updateData).toHaveProperty('client_secret', 'new-secret-value');
  });
});
