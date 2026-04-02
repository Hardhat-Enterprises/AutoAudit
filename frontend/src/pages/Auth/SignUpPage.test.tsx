import React from 'react';
import { describe, test, expect, vi, afterEach } from 'vitest';
import { cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import SignUpPage from './SignUpPage';

describe('SignUpPage', () => {
  afterEach(() => {
    cleanup();
  });

  test('renders sign-up layout and create account heading', () => {
    render(
      <MemoryRouter>
        <SignUpPage onSignUp={vi.fn()} onBackToLogin={vi.fn()} />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: /start your compliance journey/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument();
  });

  test('calls onSignUp and clears form fields on success', async () => {
    const onSignUp = vi.fn().mockResolvedValue(undefined);
    const onBackToLogin = vi.fn();
    render(
      <MemoryRouter>
        <SignUpPage onSignUp={onSignUp} onBackToLogin={onBackToLogin} />
      </MemoryRouter>
    );

    await userEvent.type(screen.getByPlaceholderText(/first name/i), 'Sam');
    await userEvent.type(screen.getByPlaceholderText(/last name/i), 'Lee');
    await userEvent.type(screen.getByPlaceholderText(/your\.email@company\.com/i), 'sam@example.com');
    await userEvent.type(screen.getByPlaceholderText(/enter your organization name/i), 'OrgCo');
    await userEvent.type(screen.getByPlaceholderText(/create a strong password/i), 'Password1!');
    await userEvent.type(screen.getByPlaceholderText(/confirm your password/i), 'Password1!');
    await userEvent.click(screen.getByRole('checkbox', { name: /i agree to the/i }));
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(onSignUp).toHaveBeenCalledWith(
        expect.objectContaining({
          firstName: 'Sam',
          lastName: 'Lee',
          email: 'sam@example.com',
          organizationName: 'OrgCo',
          password: 'Password1!',
          confirmPassword: 'Password1!',
          agreeTerms: true,
        })
      );
    });

    expect(screen.getByPlaceholderText(/first name/i)).toHaveValue('');
  });

  test('shows friendly message when onSignUp fails with REGISTER_USER_ALREADY_EXISTS', async () => {
    const onSignUp = vi.fn().mockRejectedValue(new Error('REGISTER_USER_ALREADY_EXISTS'));
    render(
      <MemoryRouter>
        <SignUpPage onSignUp={onSignUp} onBackToLogin={vi.fn()} />
      </MemoryRouter>
    );

    await userEvent.type(screen.getByPlaceholderText(/first name/i), 'Sam');
    await userEvent.type(screen.getByPlaceholderText(/last name/i), 'Lee');
    await userEvent.type(screen.getByPlaceholderText(/your\.email@company\.com/i), 'dup@example.com');
    await userEvent.type(screen.getByPlaceholderText(/enter your organization name/i), 'Org');
    await userEvent.type(screen.getByPlaceholderText(/create a strong password/i), 'Password1!');
    await userEvent.type(screen.getByPlaceholderText(/confirm your password/i), 'Password1!');
    await userEvent.click(screen.getByRole('checkbox', { name: /i agree to the/i }));
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));

    expect(
      await screen.findByText(/an account with this email already exists/i)
    ).toBeInTheDocument();
  });

  test('invokes onBackToLogin from Sign In control', async () => {
    const onBackToLogin = vi.fn();
    render(
      <MemoryRouter>
        <SignUpPage onSignUp={vi.fn()} onBackToLogin={onBackToLogin} />
      </MemoryRouter>
    );
    await userEvent.click(within(screen.getByRole('main')).getByRole('button', { name: /^sign in$/i }));
    expect(onBackToLogin).toHaveBeenCalledTimes(1);
  });
});
