# Frontend Test Gate

## Overview

This document covers the decisions and reasoning behind the frontend CI test gate added as part of the DevSecOps initiative.

The goal was to establish a baseline of automated checks that run on every pull request and block merging if something is broken. The tests act as guardrails. If a future change causes a regression, the failing test names tell you exactly what broke and where, rather than it surfacing in production.

## Why Vitest

The frontend runs on Vite, and Vitest is its native test runner. It reuses the same transform pipeline so TypeScript works without any additional config. The API mirrors Jest so the tests are readable and familiar. It was the obvious choice for this stack.

## CI Gate (`frontend.yml`)

Added a `build-and-test` job that runs on every PR targeting `main` and blocks merging if any step fails.

**TypeScript type check**
```yaml
- name: TypeScript type check
  run: npx tsc --noEmit
```
Catches type errors before they reach code review. If a type mismatch is introduced, this step fails in CI before anything is merged.

**Unit tests**
```yaml
- name: Run unit tests
  run: npm test -- --reporter=verbose
  env:
    VITE_API_URL: http://localhost:8000
```
`--reporter=verbose` makes individual test names visible in the workflow log so it is immediately clear what behaviour regressed. `VITE_API_URL` is injected here because `.env.test` is gitignored and cannot be committed. The API client throws at load time without it.

**Production build**
```yaml
- name: Build
  run: npm run build
```
Confirms the app compiles. A build can fail for reasons that type checking and unit tests won't catch, unresolved imports, invalid config, missing assets. This step closes that gap.

## Vitest Configuration (`vite.config.ts`)

```ts
test: {
  environment: 'jsdom',
  setupFiles: ['./src/setupTests.ts'],
  globals: true,
}
```

`environment: 'jsdom'` gives tests access to a browser-like DOM so React components can render. Without it Vitest runs in Node and `@testing-library/react` fails entirely.

`setupFiles` loads `@testing-library/jest-dom` before every suite, which adds matchers like `toBeInTheDocument` and `toHaveClass`.

`globals: true` makes `describe`, `it`, `expect` and `vi` available without imports in every file.

## What Was Fixed

Three existing test files had broken queries because `LandingHeader` renders a "Sign In" button in the nav bar, and the pages under test also render one in their forms. `getByRole` throws when it finds more than one match. Fixed by scoping queries with `within()` or switching to `getAllByRole()`. The assertions themselves did not change.

## What Was Added

**`src/utils/helpers.test.ts` (35 tests)**
Pure utility functions with no dependencies. Covers `validateEmail`, all GMT and AEST date/time formatters, and `truncateString`.

**`src/utils/api.test.ts` (27 tests)**
The evidence normalisation strips various bullet formats and splits on newlines and semicolons, easy to break with a regex change. `parseApiError` has a four-level message fallback chain that is not obvious from reading the code. Both are covered in full.

**`src/api/client.test.ts` (20 tests)**
Every API call in the frontend goes through this file. Tests use `vi.stubGlobal('fetch', vi.fn())` to intercept network calls. Covers `APIError` behaviour, URL construction, input validation, request shape, auth header injection, error handling, and 204 No Content responses.

**`src/components/Dropdown.test.tsx` (19 tests)**
Dropdown state is easy to break silently. Covers rendering, open/close via click and Escape key, click-outside, disabled state, option selection, `aria-expanded`, `aria-selected`, and theming.

**`src/context/AuthContext.test.tsx` (16 tests)**
Every protected page depends on this context. The original file had one placeholder test, replaced with a full suite covering the entire auth lifecycle. Covers the provider guard, credential loading from storage on mount, 401 clearing auth state, logout, login with token persistence, and `loginWithAccessToken`.

**`src/pages/Scans/ScanDetailPage.test.tsx` (16 tests)**
The page contains private functions that compute display values from raw API data. Tested indirectly through the rendered DOM. Covers loading and error states, status badge text for all scan states, result badge text, skipped result filtering, and numeric sort order (`1.1, 1.2, 1.10, 2.1`).

**`src/pages/Auth/components/SignupFormPanel.test.tsx` (10 tests, 4 added)**
Added `submitError` prop display, password visibility toggles for both fields independently, and error clearing on input.

**`src/pages/Connections/ConnectionsPage.test.tsx` (10 tests)**
Focused on the logic most likely to regress. A 400 API error must show a specific auth message rather than a raw string. Clicking Edit must populate the client secret with a mask. Submitting the edit form without changing the mask must omit `client_secret` from the payload.

**`src/pages/AccountPage.test.tsx` (9 tests)**
The display name has a five-level fallback chain that is easy to break silently. Logout is best-effort and must clear local auth and navigate even if the API call fails.

**`src/pages/SettingsPage.test.tsx` (8 tests)**
The `hasChanges` flag drives whether Save and Reset are enabled. Covers the full enable/disable lifecycle and the `updateSettings` call with the correct payload.

**`src/pages/Contact/ContactPage.test.tsx` (5 tests)**
The page maps camelCase form fields to snake_case for the API and appends `source: 'website'`. A regression here produces a malformed payload with no visible error to the user. The 5-second success message timer is tested by spying on `setTimeout`, capturing the callback, and invoking it via `act()`.

## Test Count Summary

| File | Tests | What it guards |
|---|---|---|
| `src/utils/helpers.test.ts` | 35 | Email validation, date/time formatters (GMT + AEST), string truncation |
| `src/utils/api.test.ts` | 27 | Evidence normalisation, error message parsing fallback chain |
| `src/api/client.test.ts` | 20 | HTTP client, auth headers, error handling, request shape, 204 handling |
| `src/components/Dropdown.test.tsx` | 19 | Open/close, keyboard, selection, accessibility attributes |
| `src/context/AuthContext.test.tsx` | 16 | Login, logout, token persistence, 401 clears auth state |
| `src/pages/Scans/ScanDetailPage.test.tsx` | 16 | Status labels, result badges, skipped filtering, sort order |
| `src/pages/Auth/components/SignupFormPanel.test.tsx` | 10 | Form validation, password visibility toggles, error display |
| `src/pages/Connections/ConnectionsPage.test.tsx` | 10 | Error messages, client secret masking, edit payload omits unchanged secret |
| `src/pages/AccountPage.test.tsx` | 9 | Display name fallback chain, logout (success + best-effort failure) |
| `src/pages/SettingsPage.test.tsx` | 8 | Save/Reset enable logic, settings API call, error handling |
| `src/pages/Auth/GoogleCallbackPage.test.tsx` | 6 | OAuth callback handling |
| `src/pages/Auth/SignInPanel.test.tsx` | 6 | Sign-in form submission, error display |
| `src/pages/Contact/ContactPage.test.tsx` | 5 | Field name transforms, API payload shape, success message timer |
| `src/pages/Admin/ContactAdminPage.test.tsx` | 4 | Admin access guard, submission list rendering |
| `src/pages/Auth/SignUpPage.test.tsx` | 4 | Sign-up form rendering and routing |
| `src/pages/Auth/components/AuthBrandComponents.test.tsx` | 3 | Brand panel rendering |
| `src/pages/Auth/LoginPage.test.tsx` | 2 | Login page rendering |
| `src/App.test.tsx` | 2 | Route rendering |
| **Total** | **201** | |

## Running Tests Locally

```bash
cd frontend
npm install
npm test
```

To match CI output exactly:

```bash
VITE_API_URL=http://localhost:8000 npm test -- --reporter=verbose
```

Type check only:

```bash
npx tsc --noEmit
```
