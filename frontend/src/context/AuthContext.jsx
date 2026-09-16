import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('vynk_token'));
  const [isLoading, setIsLoading] = useState(true);

  // Load active user profile if token exists on mount
  useEffect(() => {
    async function initAuth() {
      const storedToken = localStorage.getItem('vynk_token');
      if (storedToken) {
        try {
          const profile = await authService.getMe();
          setUser(profile);
          setToken(storedToken);
        } catch (err) {
          console.warn('Session expired or invalid:', err.message);
          localStorage.removeItem('vynk_token');
          setUser(null);
          setToken(null);
        }
      }
      setIsLoading(false);
    }

    initAuth();

    // Listen for 401 unauthorized broadcasts
    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
    };
    window.addEventListener('vynk:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('vynk:unauthorized', handleUnauthorized);
  }, []);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const result = await authService.login(email, password);
      localStorage.setItem('vynk_token', result.access_token);
      setToken(result.access_token);

      // Fetch complete user profile with role structures & trust score
      const profile = await authService.getMe();
      setUser(profile);
      return profile;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (formData) => {
    setIsLoading(true);
    try {
      const result = await authService.register(formData);
      localStorage.setItem('vynk_token', result.access_token);
      setToken(result.access_token);

      // Fetch complete user profile
      const profile = await authService.getMe();
      setUser(profile);
      return profile;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('vynk_token');
    setUser(null);
    setToken(null);
  };

  const refreshUser = async () => {
    if (!token) return;
    try {
      const updated = await authService.getMe();
      setUser(updated);
    } catch (err) {
      console.error('Failed to refresh user:', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
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
