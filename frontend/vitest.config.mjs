/**
 * Vitest config (ESM). Used when running `npm run test`.
 * Kept as .mjs so Node loads it as ESM and avoids esbuild/CJS issues with plugins.
 * Setup and test files are TypeScript (.ts / .tsx).
 */
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
    globals: false,
  },
});
