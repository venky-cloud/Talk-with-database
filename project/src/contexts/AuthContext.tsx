import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

type AuthContextType = {
  isAuthenticated: boolean;
  login: (token?: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const flag = localStorage.getItem('auth_token');
    setIsAuthenticated(!!flag);
  }, []);

  const value = useMemo(
    () => ({
      isAuthenticated,
      login: (token?: string) => {
        localStorage.setItem('auth_token', token || 'demo');
        setIsAuthenticated(true);
      },
      logout: () => {
        localStorage.removeItem('auth_token');
        setIsAuthenticated(false);
      },
    }),
    [isAuthenticated]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
