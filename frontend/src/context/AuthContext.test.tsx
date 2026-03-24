import React from 'react';
import { describe, test, expect, afterEach } from 'vitest';
import { cleanup, render } from '@testing-library/react';
import { useAuth } from './AuthContext';

function Consumer() {
  useAuth();
  return null;
}

describe('AuthContext', () => {
  afterEach(() => {
    cleanup();
  });

  test('useAuth throws when used outside AuthProvider', () => {
    expect(() => render(<Consumer />)).toThrow(/useAuth must be used within an AuthProvider/i);
  });
});
