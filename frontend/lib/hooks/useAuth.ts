'use client';

import { useUser, getAccessToken } from '@auth0/nextjs-auth0/client';
import { useContext, createContext, useCallback } from 'react';

// Logout options type
interface LogoutOptions {
  logoutParams?: {
    returnTo?: string;
  };
}

// Auth context type
interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: {
    name?: string;
    email?: string;
    picture?: string;
    sub?: string;
  } | undefined;
  loginWithRedirect: () => void;
  logout: (options?: LogoutOptions) => void;
  getAccessTokenSilently: () => Promise<string>;
}

// Create context for mock auth
export const MockAuthContext = createContext<AuthContextType | null>(null);

/**
 * Custom auth hook that works with both real Auth0 and mock auth
 * When Auth0 is not configured, it uses a mock context
 */
export function useAuth(): AuthContextType {
  // Try to get mock context first
  const mockContext = useContext(MockAuthContext);

  // If mock context exists, use it (dev mode without Auth0)
  if (mockContext) {
    return mockContext;
  }

  // Otherwise, use Auth0 nextjs-auth0
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const { user, isLoading, error } = useUser();

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const loginWithRedirect = useCallback(() => {
    // Use <a> tag navigation for auth routes as recommended by Auth0
    window.location.href = '/auth/login';
  }, []);

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const logout = useCallback((options?: LogoutOptions) => {
    const returnTo = options?.logoutParams?.returnTo || window.location.origin;
    window.location.href = `/auth/logout?returnTo=${encodeURIComponent(returnTo)}`;
  }, []);

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const getAccessTokenSilently = useCallback(async (): Promise<string> => {
    try {
      const token = await getAccessToken();
      return token || '';
    } catch {
      console.error('Failed to get access token');
      return '';
    }
  }, []);

  if (error) {
    console.error('Auth error:', error);
  }

  return {
    isAuthenticated: !!user,
    isLoading,
    user: user ? {
      name: user.name || undefined,
      email: user.email || undefined,
      picture: user.picture || undefined,
      sub: user.sub || undefined,
    } : undefined,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
  };
}
