import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ScanDetailPage from './ScanDetailPage';

// Mock react-router-dom hooks so we control the scanId param.
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useParams: vi.fn().mockReturnValue({ scanId: '42' }),
    useNavigate: vi.fn().mockReturnValue(vi.fn()),
  };
});

// Mock AuthContext so it never touches the real token storage.
vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn().mockReturnValue({ token: 'test-token' }),
}));

// Mock api/client so client.ts is never loaded (avoids VITE_API_URL throw).
vi.mock('../../api/client', () => ({
  getScan: vi.fn(),
}));

import { getScan } from '../../api/client';

// Minimal scan object that satisfies the ScanDetail type used in the component.
function makeScan(overrides: Record<string, unknown> = {}) {
  return {
    id: 42,
    status: 'completed',
    benchmark: 'CIS Microsoft 365',
    version: 'v3.0',
    connection_name: 'Test Connection',
    started_at: '2026-01-17T00:00:00Z',
    finished_at: '2026-01-17T01:00:00Z',
    total_controls: 3,
    passed_count: 2,
    failed_count: 1,
    error_count: 0,
    skipped_count: 0,
    results: [],
    ...overrides,
  };
}

function renderPage() {
  return render(
    <MemoryRouter>
      <ScanDetailPage />
    </MemoryRouter>
  );
}

// Wait until the loading spinner disappears (initial load complete).
function waitForLoaded() {
  return waitFor(() =>
    expect(screen.queryByText(/loading scan details/i)).not.toBeInTheDocument()
  );
}

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// --- Loading state ---

describe('ScanDetailPage loading state', () => {
  it('shows a loading indicator while the scan is being fetched', () => {
    // Never resolves — keeps the component in loading state
    vi.mocked(getScan).mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading scan details/i)).toBeInTheDocument();
  });
});

// --- Error state ---

describe('ScanDetailPage error state', () => {
  it('shows an error message when getScan rejects', async () => {
    vi.mocked(getScan).mockRejectedValue(new Error('Network failure'));
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/failed to load scan/i)).toBeInTheDocument()
    );
  });

  it('displays the specific error message from the rejection', async () => {
    vi.mocked(getScan).mockRejectedValue(new Error('Scan not found'));
    renderPage();
    await waitFor(() =>
      expect(screen.getByText('Scan not found')).toBeInTheDocument()
    );
  });
});

// --- Scan details rendering ---

describe('ScanDetailPage scan details', () => {
  it('renders the scan benchmark name', async () => {
    vi.mocked(getScan).mockResolvedValue(makeScan());
    renderPage();
    await waitForLoaded();
    expect(screen.getByRole('heading', { name: /CIS Microsoft 365/i })).toBeInTheDocument();
  });

  it('renders the connection name', async () => {
    vi.mocked(getScan).mockResolvedValue(makeScan());
    renderPage();
    await waitForLoaded();
    expect(screen.getByText('Test Connection')).toBeInTheDocument();
  });
});

// --- getStatusText (private — tested via the rendered status badge) ---

describe('getStatusText', () => {
  it.each([
    ['completed', 'Completed'],
    ['failed', 'Failed'],
    ['running', 'Running'],
    [undefined, 'Pending'],
  ])('status %s renders badge text "%s"', async (status, expectedText) => {
    vi.mocked(getScan).mockResolvedValue(makeScan({ status }));
    const { container } = renderPage();
    await waitForLoaded();
    // Scope to the status badge to avoid matching stat card labels or meta labels
    // that coincidentally share the same text (e.g. "Failed" stat label, "Completed" meta label).
    const badge = container.querySelector('.status-badge');
    expect(within(badge as HTMLElement).getByText(expectedText as string)).toBeInTheDocument();
  });
});

// --- getResultBadgeText (private — tested via rendered result cards) ---

describe('getResultBadgeText', () => {
  it.each([
    ['passed', 'Pass'],
    ['failed', 'Fail'],
    ['error', 'Error'],
    ['pending', 'Pending'],
  ])('result status %s renders badge text "%s"', async (status, expectedText) => {
    vi.mocked(getScan).mockResolvedValue(
      makeScan({
        status: 'completed',
        results: [{ control_id: '1.1', status, title: 'Test control' }],
      })
    );
    renderPage();
    await waitForLoaded();
    expect(screen.getByText(expectedText)).toBeInTheDocument();
  });
});

// --- Skipped results ---

describe('ScanDetailPage result filtering', () => {
  it('does not render results with status "skipped"', async () => {
    vi.mocked(getScan).mockResolvedValue(
      makeScan({
        status: 'completed',
        results: [
          { control_id: '1.1', status: 'passed', title: 'Visible control' },
          { control_id: '1.2', status: 'skipped', title: 'Hidden skipped control' },
        ],
      })
    );
    renderPage();
    await waitForLoaded();

    expect(screen.getByText('Visible control')).toBeInTheDocument();
    expect(screen.queryByText('Hidden skipped control')).not.toBeInTheDocument();
  });
});

// --- compareControlIdAscending (private — tested via DOM order of rendered results) ---

describe('compareControlIdAscending', () => {
  it('renders results sorted by control ID in ascending order', async () => {
    vi.mocked(getScan).mockResolvedValue(
      makeScan({
        status: 'completed',
        results: [
          { control_id: '2.1', status: 'passed', title: 'Control 2.1' },
          { control_id: '1.10', status: 'passed', title: 'Control 1.10' },
          { control_id: '1.1', status: 'passed', title: 'Control 1.1' },
          { control_id: '1.2', status: 'passed', title: 'Control 1.2' },
        ],
      })
    );

    const { container } = renderPage();
    await waitForLoaded();

    const controlIdSpans = container.querySelectorAll('.control-id');
    const renderedIds = Array.from(controlIdSpans).map((el) => el.textContent);
    expect(renderedIds).toEqual(['1.1', '1.2', '1.10', '2.1']);
  });

  it('sorts numeric segments correctly so 1.10 comes after 1.9', async () => {
    vi.mocked(getScan).mockResolvedValue(
      makeScan({
        status: 'completed',
        results: [
          { control_id: '1.10', status: 'passed', title: 'Control 1.10' },
          { control_id: '1.9', status: 'passed', title: 'Control 1.9' },
        ],
      })
    );

    const { container } = renderPage();
    await waitForLoaded();

    const controlIdSpans = container.querySelectorAll('.control-id');
    const renderedIds = Array.from(controlIdSpans).map((el) => el.textContent);
    expect(renderedIds).toEqual(['1.9', '1.10']);
  });
});
