import React from 'react';
import { describe, test, expect, vi, afterEach } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SignupFormPanel from './SignupFormPanel';
import type { SignUpFormData } from '../signUpTypes';
import { expectedGoogleAuthorizeUrl } from '../../../test/oauthTestHelpers';

const emptyForm: SignUpFormData = {
  firstName: '',
  lastName: '',
  email: '',
  organizationName: '',
  password: '',
  confirmPassword: '',
};

function renderPanel(overrides?: Partial<SignUpFormData>) {
  const formData = { ...emptyForm, ...overrides };
  const onFormChange = vi.fn();
  const onSubmit = vi.fn().mockResolvedValue(undefined);
  const onBackToLogin = vi.fn();
  render(
    <SignupFormPanel
      formData={formData}
      onFormChange={onFormChange}
      onSubmit={onSubmit}
      onBackToLogin={onBackToLogin}
      submitError=""
    />
  );
  return { onFormChange, onSubmit, onBackToLogin };
}

describe('SignupFormPanel', () => {
  afterEach(() => {
    cleanup();
  });

  test('renders create account form', () => {
    renderPanel();
    expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/first name/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  test('shows error when terms are not accepted', async () => {
    const { onSubmit } = renderPanel({
      firstName: 'A',
      lastName: 'B',
      email: 'a@b.com',
      organizationName: 'Org',
      password: 'same123',
      confirmPassword: 'same123',
    });

    await userEvent.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/please agree to the terms/i);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('shows error when passwords do not match', async () => {
    const { onSubmit } = renderPanel({
      firstName: 'A',
      lastName: 'B',
      email: 'a@b.com',
      organizationName: 'Org',
      password: 'onepassword',
      confirmPassword: 'otherpassword',
    });

    await userEvent.click(
      screen.getByRole('checkbox', {
        name: /i agree to the/i,
      })
    );
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByText(/these passwords do not match/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('calls onSubmit with payload when form is valid', async () => {
    const { onSubmit } = renderPanel({
      firstName: 'Jane',
      lastName: 'Doe',
      email: 'jane@example.com',
      organizationName: 'Acme',
      password: 'SecurePass1',
      confirmPassword: 'SecurePass1',
    });

    await userEvent.click(screen.getByRole('checkbox', { name: /i agree to the/i }));
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      firstName: 'Jane',
      lastName: 'Doe',
      email: 'jane@example.com',
      organizationName: 'Acme',
      password: 'SecurePass1',
      confirmPassword: 'SecurePass1',
      agreeTerms: true,
    });
  });

  test('invokes onBackToLogin from Sign In link', async () => {
    const { onBackToLogin } = renderPanel();
    await userEvent.click(screen.getByRole('button', { name: /^sign in$/i }));
    expect(onBackToLogin).toHaveBeenCalledTimes(1);
  });

  test('Google sign-up button assigns authorize URL', async () => {
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

    renderPanel();
    await userEvent.click(screen.getByRole('button', { name: /^google$/i }));

    expect(assignSpy).toHaveBeenCalledWith(expectedGoogleAuthorizeUrl());

    Object.defineProperty(window, 'location', {
      configurable: true,
      writable: true,
      value: originalLocation,
    });
  });
});
