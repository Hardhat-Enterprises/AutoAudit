import React, { createContext, useContext, useState, useEffect } from "react";
import { login as apiLogin, getCurrentUser, APIError } from "../api/client";

const AuthContext = createContext(null);

const TOKEN_KEY = "token";
const USER_KEY = "user";

function safeJsonParse(value) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function getStoredToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY) || window.sessionStorage.getItem(TOKEN_KEY);
}

function getStoredUser() {
  if (typeof window === "undefined") return null;
  return (
    safeJsonParse(window.localStorage.getItem(USER_KEY)) ||
    safeJsonParse(window.sessionStorage.getItem(USER_KEY))
  );
}

function clearStoredAuth() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  window.sessionStorage.removeItem(TOKEN_KEY);
  window.sessionStorage.removeItem(USER_KEY);
}

function persistAuth(accessToken, userData, remember) {
  if (typeof window === "undefined") return;
  const storage = remember ? window.localStorage : window.sessionStorage;
  const other = remember ? window.sessionStorage : window.localStorage;

  storage.setItem(TOKEN_KEY, accessToken);
  storage.setItem(USER_KEY, JSON.stringify(userData));

  // Ensure we don't have stale auth state in the other storage
  other.removeItem(TOKEN_KEY);
  other.removeItem(USER_KEY);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [token, setToken] = useState(() => getStoredToken());
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!token && !!user;

  // Validate token on mount
  useEffect(() => {
    async function validateToken() {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const userData = await getCurrentUser(token);
        setUser(userData);

        // Refresh cached user in whichever storage currently holds the token
        const inLocal = typeof window !== "undefined" && window.localStorage.getItem(TOKEN_KEY) === token;
        const storage = typeof window !== "undefined" && inLocal ? window.localStorage : window.sessionStorage;
        if (typeof window !== "undefined") {
          storage.setItem(USER_KEY, JSON.stringify(userData));
        }
      } catch (error) {
        // Only clear auth when the backend confirms token is invalid/expired
        if (error instanceof APIError && (error.status === 401 )) {
          clearStoredAuth();
          setToken(null);
          setUser(null);
        }
      } finally {
        setIsLoading(false);
      }
    }

    validateToken();
  }, [token]);

  async function login(email, password, remember = true) {
    const response = await apiLogin(email, password);
    const accessToken = response.access_token;

    // Fetch user data
    const userData = await getCurrentUser(accessToken);
    persistAuth(accessToken, userData, remember);

    setToken(accessToken);
    setUser(userData);
    return userData;
  }

  function logout() {
    clearStoredAuth();
    setToken(null);
    setUser(null);
  }

  const value = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
