import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, getCurrentUser } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
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
      } catch (error) {
        // Token invalid, clear it
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    validateToken();
  }, [token]);

  async function login(email, password) {
    const response = await apiLogin(email, password);
    const accessToken = response.access_token;

    localStorage.setItem('token', accessToken);
    setToken(accessToken);

    // Fetch user data
    const userData = await getCurrentUser(accessToken);
    setUser(userData);

    return userData;
  }

  function logout() {
    localStorage.removeItem('token');
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
