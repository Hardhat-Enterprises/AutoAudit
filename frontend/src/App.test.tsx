import React from 'react';
import { test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import App from './App';

type TestWrapperProps = {
  children: React.ReactNode;
  initialEntries?: string[];
}

function TestWrapper({ children, initialEntries = ['/'] }: TestWrapperProps) {
  return (
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </MemoryRouter>
  );
}

test('renders login page at /login', () => {
  render(<App />, {
    wrapper: (props) => <TestWrapper {...props} initialEntries={['/login']} />,
  });
  const welcomeHeading = screen.getByRole('heading', { name: /welcome back/i });
  expect(welcomeHeading).toBeInTheDocument();
  expect(screen.getAllByRole('button', { name: /sign in/i }).length).toBeGreaterThan(0);
});

test('renders app with AutoAudit branding', () => {
  render(<App />, {
    wrapper: TestWrapper,
  });
  const headings = screen.getAllByText(/autoaudit/i);
  expect(headings.length).toBeGreaterThan(0);
  expect(headings[0]).toBeInTheDocument();
});
