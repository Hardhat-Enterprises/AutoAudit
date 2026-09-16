import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from './Dashboard';
import { useAuth } from '../context/AuthContext';
import {
  getBenchmarks as mockGetBenchmarks,
  getConnections as mockGetConnections,
  getScans as mockGetScans,
  getScan as mockGetScan,
} from '../api/client';

// Mock AuthContext so we can drive `isAuthenticated` independently of
// `token`, which is always null under cookie-based auth (see
// AuthContext.tsx) -- that decoupling is exactly what these tests exist
// to cover.
vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

// Mock api/client so client.ts (and its VITE_API_URL read) is never
// loaded, and so we can assert on / control what the dashboard fetches.
vi.mock('../api/client', () => ({
  getBenchmarks: vi.fn(),
  getConnections: vi.fn(),
  getScans: vi.fn(),
  getScan: vi.fn(),
}));

function mockAuth(overrides: Partial<ReturnType<typeof useAuth>> = {}) {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    completeOAuthLogin: vi.fn(),
    logout: vi.fn(),
    ...overrides,
  });
}

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard isDarkMode={false} />
    </MemoryRouter>,
  );
}

function waitForLoaded() {
  return waitFor(() =>
    expect(
      screen.queryByText(/loading latest results/i),
    ).not.toBeInTheDocument(),
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(mockGetBenchmarks).mockResolvedValue([]);
  vi.mocked(mockGetConnections).mockResolvedValue([]);
  vi.mocked(mockGetScans).mockResolvedValue([]);
  vi.mocked(mockGetScan).mockResolvedValue({ id: 1, results: [] });
});

afterEach(cleanup);

// Regression coverage for a bug where the dashboard's data-loading effects
// were gated on `token` instead of `isAuthenticated`. Since the frontend
// migrated to cookie-based auth, `token` is permanently null (see
// AuthContext.tsx), so `if (!token) return;` bailed out of both effects
// immediately -- no authenticated user could ever load dashboard data, and
// the "Loading latest results…" spinner spun forever. Gating on
// `isAuthenticated` instead fixes this without weakening any security
// boundary, since `ProtectedRoute` already ensures Dashboard only mounts
// for authenticated users.
describe('Dashboard data loading', () => {
  it('loads scans, connections and benchmarks for an authenticated (cookie-based) user', async () => {
    mockAuth({ isAuthenticated: true, token: null });

    renderDashboard();

    await waitForLoaded();

    expect(mockGetScans).toHaveBeenCalledWith(null);
    expect(mockGetConnections).toHaveBeenCalledWith(null);
    expect(mockGetBenchmarks).toHaveBeenCalledWith(null);
  });

  it('does not fetch dashboard data when the user is not authenticated', async () => {
    mockAuth({ isAuthenticated: false, token: null });

    renderDashboard();

    // Give any (incorrectly firing) effect a tick to run before asserting
    // the negative.
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(mockGetScans).not.toHaveBeenCalled();
    expect(mockGetConnections).not.toHaveBeenCalled();
    expect(mockGetBenchmarks).not.toHaveBeenCalled();
  });
});
