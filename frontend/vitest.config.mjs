/**
 * Vitest config (ESM). Used when running `npm run test`.
 * Kept as .mjs so Node loads it as ESM and avoids esbuild/CJS issues with plugins.
 * Setup and test files are TypeScript (.ts / .tsx).
 *
 * Env: same rules as Vite dev — `loadEnv(mode, cwd)` loads `.env`, `.env.local`, `.env.[mode]`, etc.
 * If `VITE_API_URL` is missing (e.g. no `.env` in CI), fall back to the value in committed `.env.example`
 * so `import.meta.env.VITE_API_URL` matches onboarding defaults, not a hard-coded test host.
 */
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { defineConfig } from 'vitest/config';
import { loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

function readViteApiUrlFromEnvExample() {
  const p = resolve(process.cwd(), '.env.example');
  if (!existsSync(p)) return '';
  for (const line of readFileSync(p, 'utf8').split('\n')) {
    const t = line.trim();
    if (t.startsWith('#') || !t) continue;
    const eq = t.indexOf('=');
    if (eq === -1) continue;
    const key = t.slice(0, eq).trim();
    if (key !== 'VITE_API_URL') continue;
    return t
      .slice(eq + 1)
      .trim()
      .replace(/^["']|["']$/g, '');
  }
  return '';
}

export default defineConfig(({ mode }) => {
  const loaded = loadEnv(mode, process.cwd(), '');
  const viteApiUrl = loaded.VITE_API_URL || readViteApiUrlFromEnvExample();

  /** Mirror Vite’s import.meta.env injection for VITE_* keys used in tests and components. */
  const define = {};
  for (const [key, value] of Object.entries(loaded)) {
    if (key.startsWith('VITE_')) {
      define[`import.meta.env.${key}`] = JSON.stringify(value);
    }
  }
  if (!loaded.VITE_API_URL && viteApiUrl) {
    define['import.meta.env.VITE_API_URL'] = JSON.stringify(viteApiUrl);
  }

  return {
    plugins: [react()],
    define,
    test: {
      environment: 'jsdom',
      setupFiles: ['./vitest.setup.ts'],
      include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
      globals: false,
    },
  };
});
