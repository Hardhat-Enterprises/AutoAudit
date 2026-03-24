import React from 'react';
import { describe, test, expect, afterEach } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LoginHeader from './LoginHeader';
import BrandPanel from './BrandPanel';
import SignupBrandPanel from './SignupBrandPanel';

describe('Auth presentational components', () => {
  afterEach(() => {
    cleanup();
  });

  describe('LoginHeader', () => {
    test('renders logo and primary nav links', () => {
      render(
        <MemoryRouter>
          <LoginHeader />
        </MemoryRouter>
      );
      expect(screen.getByRole('link', { name: /autoaudit home/i })).toBeInTheDocument();
      expect(screen.getByRole('navigation', { name: /primary navigation/i })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /^home$/i })).toHaveAttribute('href', '/');
      expect(screen.getByRole('link', { name: /^about$/i })).toBeInTheDocument();
    });
  });

  describe('BrandPanel', () => {
    test('renders brand title and feature highlights', () => {
      render(<BrandPanel />);
      expect(screen.getByRole('heading', { name: /access security insights anywhere/i })).toBeInTheDocument();
      expect(screen.getByText(/enterprise-grade security/i)).toBeInTheDocument();
    });
  });

  describe('SignupBrandPanel', () => {
    test('renders signup brand messaging', () => {
      render(<SignupBrandPanel />);
      expect(screen.getByRole('heading', { name: /start your compliance journey/i })).toBeInTheDocument();
      expect(screen.getByText(/setup in minutes/i)).toBeInTheDocument();
    });
  });
});
