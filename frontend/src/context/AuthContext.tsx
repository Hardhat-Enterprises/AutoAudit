import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  login as apiLogin,
  logout as apiLogout,
  getCurrentUser,
  APIError,
} from "../api/client";

/** User shape returned by `/users/me` */
export type AuthUser = {
  id?: number | string | null;
  email?: string | null;
  username?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  organization_name?: string | null;
  name?: string | null;
  role?: string | null;
  is_active?: boolean | null;
};

export type AuthContextValue = {
  user: AuthUser | null;
  /**
   * Kept for backward compatibility with any call site still reading `token`
   * off the auth context. The backend issues the session as an HttpOnly
   * cookie (PR #308), so there is no JWT the frontend can read or store any
   * more — this is always `null`. Authenticated requests still work because
   * every fetch call is made with `credentials: "include"`, which sends the
   * cookie automatically.
   */
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<AuthUser>;
  /**
   * Call after a Google OAuth redirect lands back on the frontend. The
   * backend has already set the session cookie before redirecting, so this
   * just confirms the session is live via `/users/me`.
   */
  completeOAuthLogin: () => Promise<AuthUser>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const USER_CACHE_KEY = "user";

function safeJsonParse(value: string | null): unknown {
  if (!value) return null;
  try {
    return JSON.parse(value) as unknown;
  } catch {
    return null;
  }
}

function getCachedUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const parsed = safeJsonParse(window.sessionStorage.getItem(USER_CACHE_KEY));
  if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
    return parsed as AuthUser;
  }
  return null;
}

function cacheUser(userData: AuthUser | null): void {
  if (typeof window === "undefined") return;
  try {
    if (userData) {
      window.sessionStorage.setItem(USER_CACHE_KEY, JSON.stringify(userData));
    } else {
      window.sessionStorage.removeItem(USER_CACHE_KEY);
    }
  } catch {
    // best-effort; this cache is only a paint optimisation, never the source of truth
  }
}

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  // Seed from cache so we don't flash a logged-out UI while the /users/me
  // check below is in flight. This never grants access by itself — only a
  // valid HttpOnly cookie, verified against the backend, does that.
  const [user, setUser] = useState<AuthUser | null>(() => getCachedUser());
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  useEffect(() => {
    let cancelled = false;

    async function validateSession() {
      try {
        const userData = (await getCurrentUser(null)) as AuthUser;
        if (!cancelled) {
          setUser(userData);
          cacheUser(userData);
        }
      } catch (error) {
        if (!cancelled && error instanceof APIError && error.status === 401) {
          setUser(null);
          cacheUser(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void validateSession();
    return () => {
      cancelled = true;
    };
  }, []);

  async function login(
    email: string,
    password: string,
    remember?: boolean,
  ): Promise<AuthUser> {
    // `remember` is accepted for compatibility with the login form
    // (SignInPanel, App.tsx). It's currently a no-op: the session cookie's
    // lifetime is fixed server-side by ACCESS_TOKEN_EXPIRE_MINUTES and
    // doesn't vary based on this flag. Making "remember me" genuinely
    // extend the session would require the login endpoint to accept and
    // honor it — out of scope for this fix.
    void remember;

    // Sets the HttpOnly session cookie via Set-Cookie; there is no token in
    // the response body for JS to read.
    await apiLogin(email, password);

    const userData = (await getCurrentUser(null)) as AuthUser;
    setUser(userData);
    cacheUser(userData);
    return userData;
  }

  async function completeOAuthLogin(): Promise<AuthUser> {
    const userData = (await getCurrentUser(null)) as AuthUser;
    setUser(userData);
    cacheUser(userData);
    return userData;
  }

  const logoutInFlight = useRef<Promise<void> | null>(null);

  async function logout(): Promise<void> {
    // If a logout is already in flight (e.g. a double-click, or the logout
    // control firing twice), reuse that same promise instead of sending a
    // second /v1/auth/logout request — the second request would find the
    // cookie already cleared and come back 401.
    if (logoutInFlight.current) {
      return logoutInFlight.current;
    }

    const run = (async () => {
      try {
        await apiLogout();
      } catch (error) {
        // The session may already be invalidated (expired cookie, or a
        // stray duplicate call) — that's still a successful logout from the
        // user's point of view, so we swallow a 401 here rather than
        // letting it surface as an unhandled rejection. Anything else is
        // logged for visibility.
        if (!(error instanceof APIError && error.status === 401)) {
          console.error("Logout request failed:", error);
        }
      } finally {
        // Clear local state even if the network call fails, so the UI never
        // gets stuck showing a signed-in view after the user asks to sign out.
        setUser(null);
        cacheUser(null);
        logoutInFlight.current = null;
      }
    })();

    logoutInFlight.current = run;
    return run;
  }

  const value: AuthContextValue = {
    user,
    token: null,
    isAuthenticated,
    isLoading,
    login,
    completeOAuthLogin,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}