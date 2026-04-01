import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SettingsPage from './SettingsPage';

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn().mockReturnValue({ token: 'test-token' }),
}));

vi.mock('../api/client', () => ({
  getSettings: vi.fn(),
  updateSettings: vi.fn(),
}));

import { getSettings as mockGetSettings, updateSettings as mockUpdateSettings } from '../api/client';

function renderPage() {
  return render(<SettingsPage />);
}

function waitForLoaded() {
  return waitFor(() =>
    expect(screen.queryByText(/loading settings/i)).not.toBeInTheDocument()
  );
}

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// --- Loading state ---

describe('SettingsPage loading state', () => {
  it('shows a loading indicator while settings are being fetched', () => {
    vi.mocked(mockGetSettings).mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading settings/i)).toBeInTheDocument();
  });
});

// --- Error state ---

describe('SettingsPage error state', () => {
  it('shows an error banner when getSettings rejects', async () => {
    vi.mocked(mockGetSettings).mockRejectedValue(new Error('Server error'));
    renderPage();
    await waitFor(() =>
      expect(screen.getByText('Server error')).toBeInTheDocument()
    );
  });
});

// --- hasChanges / Save + Reset buttons ---

describe('hasChanges', () => {
  it('disables Save and Reset when no changes have been made', async () => {
    vi.mocked(mockGetSettings).mockResolvedValue({ confirm_delete_enabled: true });
    renderPage();
    await waitForLoaded();

    expect(screen.getByRole('button', { name: /save/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /reset/i })).toBeDisabled();
  });

  it('enables Save and Reset after toggling the checkbox', async () => {
    vi.mocked(mockGetSettings).mockResolvedValue({ confirm_delete_enabled: true });
    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('checkbox', { name: /confirm before delete/i }));

    expect(screen.getByRole('button', { name: /save/i })).toBeEnabled();
    expect(screen.getByRole('button', { name: /reset/i })).toBeEnabled();
  });

  it('disables Save and Reset again after clicking Reset', async () => {
    vi.mocked(mockGetSettings).mockResolvedValue({ confirm_delete_enabled: true });
    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('checkbox', { name: /confirm before delete/i }));
    await userEvent.click(screen.getByRole('button', { name: /reset/i }));

    expect(screen.getByRole('button', { name: /save/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /reset/i })).toBeDisabled();
  });
});

// --- handleSave ---

describe('handleSave', () => {
  it('calls updateSettings with the toggled value', async () => {
    vi.mocked(mockGetSettings).mockResolvedValue({ confirm_delete_enabled: true });
    vi.mocked(mockUpdateSettings).mockResolvedValue({ confirm_delete_enabled: false });
    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('checkbox', { name: /confirm before delete/i }));
    await userEvent.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() =>
      expect(mockUpdateSettings).toHaveBeenCalledWith('test-token', { confirm_delete_enabled: false })
    );
  });

  it('disables Save and Reset after a successful save', async () => {
    vi.mocked(mockGetSettings).mockResolvedValue({ confirm_delete_enabled: true });
    vi.mocked(mockUpdateSettings).mockResolvedValue({ confirm_delete_enabled: false });
    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('checkbox', { name: /confirm before delete/i }));
    await userEvent.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /save/i })).toBeDisabled();
      expect(screen.getByRole('button', { name: /reset/i })).toBeDisabled();
    });
  });

  it('shows an error banner when updateSettings rejects', async () => {
    vi.mocked(mockGetSettings).mockResolvedValue({ confirm_delete_enabled: true });
    vi.mocked(mockUpdateSettings).mockRejectedValue(new Error('Save failed'));
    renderPage();
    await waitForLoaded();

    await userEvent.click(screen.getByRole('checkbox', { name: /confirm before delete/i }));
    await userEvent.click(screen.getByRole('button', { name: /save/i }));

    await waitFor(() =>
      expect(screen.getByText('Save failed')).toBeInTheDocument()
    );
  });
});
