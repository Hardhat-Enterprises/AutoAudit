import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { login as apiLogin, getCurrentUser, APIError } from "../api/client";

/** User shape returned by `/users/me` and stored in local/session storage */
export type AuthUser = {
  id?: number | string | null;
  email?: string | null;
  username?: string | null;
  name?: string | null;
  role?: string | null;
  is_active?: boolean | null;
}

export type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<AuthUser>;
  loginWithAccessToken: (accessToken: string, remember?: boolean) => Promise<AuthUser>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = "token";
const USER_KEY = "user";

function safeJsonParse(value: string | null): unknown {
  if (!value) return null;
  try {
    return JSON.parse(value) as unknown;
  } catch {
    return null;
  }
}

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY) || window.sessionStorage.getItem(TOKEN_KEY);
}

function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const fromLocal = safeJsonParse(window.localStorage.getItem(USER_KEY));
  const fromSession = safeJsonParse(window.sessionStorage.getItem(USER_KEY));
  const parsed = fromLocal ?? fromSession;
  if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
    return parsed as AuthUser;
  }
  return null;
}

function clearStoredAuth(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  window.sessionStorage.removeItem(TOKEN_KEY);
  window.sessionStorage.removeItem(USER_KEY);
}

function persistAuth(accessToken: string, userData: AuthUser, remember: boolean): void {
  if (typeof window === "undefined") return;
  const storage = remember ? window.localStorage : window.sessionStorage;
  const other = remember ? window.sessionStorage : window.localStorage;

  storage.setItem(TOKEN_KEY, accessToken);
  storage.setItem(USER_KEY, JSON.stringify(userData));

  other.removeItem(TOKEN_KEY);
  other.removeItem(USER_KEY);
}

type AuthProviderProps = {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [isLoading, setIsLoading] = useState(true);
  const skipNextValidationRef = useRef(false);

  const isAuthenticated = !!token && !!user;

  useEffect(() => {
    async function validateToken() {
      if (!token) {
        setIsLoading(false);
        return;
      }

      if (skipNextValidationRef.current) {
        skipNextValidationRef.current = false;
        setIsLoading(false);
        return;
      }

      try {
        const userData = await getCurrentUser(token);
        setUser(userData as AuthUser);

        const inLocal =
          typeof window !== "undefined" && window.localStorage.getItem(TOKEN_KEY) === token;
        const storage =
          typeof window !== "undefined" && inLocal ? window.localStorage : window.sessionStorage;
        if (typeof window !== "undefined") {
          storage.setItem(USER_KEY, JSON.stringify(userData));
        }
      } catch (error) {
        if (error instanceof APIError && error.status === 401) {
          clearStoredAuth();
          setToken(null);
          setUser(null);
        }
      } finally {
        setIsLoading(false);
      }
    }

    void validateToken();
  }, [token]);

  async function login(email: string, password: string, remember = true): Promise<AuthUser> {
    const response = await apiLogin(email, password);
    const accessToken = response.access_token;

    const userData = (await getCurrentUser(accessToken)) as AuthUser;
    persistAuth(accessToken, userData, remember);

    skipNextValidationRef.current = true;
    setToken(accessToken);
    setUser(userData);
    return userData;
  }

  async function loginWithAccessToken(accessToken: string, remember = false): Promise<AuthUser> {
    if (!accessToken) {
      throw new Error("Access token is required");
    }

    const userData = (await getCurrentUser(accessToken)) as AuthUser;
    persistAuth(accessToken, userData, remember);

    skipNextValidationRef.current = true;
    setToken(accessToken);
    setUser(userData);
    return userData;
  }

  function logout(): void {
    clearStoredAuth();
    setToken(null);
    setUser(null);
  }

  const value: AuthContextValue = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    loginWithAccessToken,
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
