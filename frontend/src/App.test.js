import { render, screen } from '@testing-library/react';
import App from './App';

test('renders autoaudit login page', () => {
  render(<App />);
  const loginHeading = screen.getByRole('heading', { name: /sign in/i });
  expect(loginHeading).toBeInTheDocument();
});

test('renders autoaudit heading', () => {
  render(<App />);
  const heading = screen.getByText(/autoaudit/i);
  expect(heading).toBeInTheDocument();
});
