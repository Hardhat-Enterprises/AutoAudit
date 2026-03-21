import React from 'react';
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import { useAuth } from '../../context/AuthContext';

vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

function setupAuthMock() {
  vi.mocked(useAuth).mockReturnValue({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    loginWithAccessToken: vi.fn(),
    logout: vi.fn(),
  });
}

function renderLogin(props?: Partial<React.ComponentProps<typeof LoginPage>>) {
  const onLogin = props?.onLogin ?? vi.fn().mockResolvedValue(undefined);
  const onSignUpClick = props?.onSignUpClick ?? vi.fn();
  return render(
    <MemoryRouter>
      <LoginPage onLogin={onLogin} onSignUpClick={onSignUpClick} />
    </MemoryRouter>
  );
}

describe('LoginPage', () => {
  beforeEach(() => {
    setupAuthMock();
  });

  afterEach(() => {
    cleanup();
  });

  test('renders sign-in layout with brand and welcome heading', () => {
    renderLogin();
    expect(screen.getByRole('heading', { name: /access security insights anywhere/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: /primary navigation/i })).toBeInTheDocument();
  });

  test('passes login and sign-up handlers to SignInPanel', async () => {
    const onLogin = vi.fn().mockResolvedValue(undefined);
    const onSignUpClick = vi.fn();
    renderLogin({ onLogin, onSignUpClick });

    await userEvent.type(screen.getByLabelText(/email address/i), 'x@y.com');
    await userEvent.type(screen.getByLabelText(/^password$/i), 'secret');
    await userEvent.click(screen.getByRole('button', { name: /^sign in$/i }));

    expect(onLogin).toHaveBeenCalled();
    await userEvent.click(screen.getByRole('button', { name: /create one/i }));
    expect(onSignUpClick).toHaveBeenCalled();
  });
});
