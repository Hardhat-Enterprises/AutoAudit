/**
 * Expected Google OAuth authorize URL — must match SignInPanel / SignupFormPanel:
 * `${import.meta.env.VITE_API_URL}/v1/auth/google/authorize`
 */
export function expectedGoogleAuthorizeUrl(): string {
  const base = import.meta.env.VITE_API_URL;
  if (base == null || String(base).trim() === '') {
    throw new Error(
      'VITE_API_URL is unset in Vitest. Use frontend/.env (see .env.example) or ensure vitest.config loads env.'
    );
  }
  return `${base}/v1/auth/google/authorize`;
}
