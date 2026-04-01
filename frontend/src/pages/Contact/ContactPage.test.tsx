import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ContactPage from './ContactPage';

// Avoid rendering unrelated nav/footer/info components
vi.mock('../Landing/components/LandingHeader', () => ({ default: () => null }));
vi.mock('../Landing/components/LandingFooter', () => ({ default: () => null }));
vi.mock('./components/ContactInfoGrid', () => ({ default: () => null }));
vi.mock('./components/FAQSection', () => ({ default: () => null }));

vi.mock('../../api/client', () => ({
  createContactSubmission: vi.fn(),
}));

import { createContactSubmission as mockCreateContactSubmission } from '../../api/client';

async function fillAndSubmit(overrides: Record<string, string> = {}) {
  const fields = {
    firstName: 'Jane',
    lastName: 'Doe',
    email: 'jane@example.com',
    subject: 'general',
    message: 'Hello there',
    ...overrides,
  };

  if (fields.firstName) await userEvent.type(screen.getByLabelText(/first name/i), fields.firstName);
  if (fields.lastName)  await userEvent.type(screen.getByLabelText(/last name/i),  fields.lastName);
  if (fields.email)     await userEvent.type(screen.getByLabelText(/email address/i), fields.email);
  if (fields.subject)   await userEvent.selectOptions(screen.getByLabelText(/subject/i), fields.subject);
  if (fields.message)   await userEvent.type(screen.getByLabelText(/message/i), fields.message);

  await userEvent.click(screen.getByRole('button', { name: /send message/i }));
}

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

// --- handleSubmit field name transforms ---

describe('handleSubmit', () => {
  it('maps camelCase field names to snake_case for the API', async () => {
    vi.mocked(mockCreateContactSubmission).mockResolvedValue(undefined);
    render(<ContactPage />);

    await fillAndSubmit();

    await waitFor(() => expect(mockCreateContactSubmission).toHaveBeenCalled());

    const payload = vi.mocked(mockCreateContactSubmission).mock.calls[0][0];
    expect(payload).toMatchObject({
      first_name: 'Jane',
      last_name: 'Doe',
      email: 'jane@example.com',
    });
  });

  it('always includes source: "website"', async () => {
    vi.mocked(mockCreateContactSubmission).mockResolvedValue(undefined);
    render(<ContactPage />);

    await fillAndSubmit();

    await waitFor(() => expect(mockCreateContactSubmission).toHaveBeenCalled());

    const payload = vi.mocked(mockCreateContactSubmission).mock.calls[0][0];
    expect(payload).toHaveProperty('source', 'website');
  });

  it('sends phone and company as null when left empty', async () => {
    vi.mocked(mockCreateContactSubmission).mockResolvedValue(undefined);
    render(<ContactPage />);

    // phone and company fields are left blank
    await fillAndSubmit();

    await waitFor(() => expect(mockCreateContactSubmission).toHaveBeenCalled());

    const payload = vi.mocked(mockCreateContactSubmission).mock.calls[0][0];
    expect(payload).toMatchObject({ phone: null, company: null });
  });
});

// --- handleFormSuccess (success message + 5-second timer) ---

describe('handleFormSuccess', () => {
  it('shows the success message after a successful submission', async () => {
    vi.mocked(mockCreateContactSubmission).mockResolvedValue(undefined);
    render(<ContactPage />);

    await fillAndSubmit();

    await waitFor(() => {
      expect(document.querySelector('.success-message')).toHaveClass('show');
    });
  });

  it('hides the success message after 5 seconds', async () => {
    vi.mocked(mockCreateContactSubmission).mockResolvedValue(undefined);

    // Spy on setTimeout to capture the callback without faking the whole timer system
    const setTimeoutSpy = vi.spyOn(globalThis, 'setTimeout');

    render(<ContactPage />);
    await fillAndSubmit();

    await waitFor(() => {
      expect(document.querySelector('.success-message')).toHaveClass('show');
    });

    // Find the 5-second callback registered by handleFormSuccess
    const fiveSecondCall = setTimeoutSpy.mock.calls.find(([, delay]) => delay === 5000);
    expect(fiveSecondCall).toBeDefined();

    // Fire the callback as React would 
    act(() => {
      (fiveSecondCall![0] as () => void)();
    });

    expect(document.querySelector('.success-message')).not.toHaveClass('show');

    setTimeoutSpy.mockRestore();
  });
});
