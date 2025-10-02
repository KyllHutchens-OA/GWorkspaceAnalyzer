'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import api from '@/lib/api';
import { syncGoogleTokensToBackend } from '@/lib/syncGoogleTokens';

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  status: AuthStatus;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        const user = session.user;
        setUser({
          id: user.id,
          email: user.email || '',
          name: user.user_metadata?.name || user.email?.split('@')[0] || '',
          picture: user.user_metadata?.avatar_url,
        });
        api.setAuthToken(session.access_token);

        // Sync Google OAuth tokens to backend for Gmail access
        await syncGoogleTokensToBackend();
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
        api.setAuthToken(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const checkAuth = async () => {
    try {
      console.log('Checking auth with Supabase...');
      const { data: { session }, error } = await supabase.auth.getSession();

      if (error) {
        console.error('Supabase session error:', error);
        setIsLoading(false);
        return;
      }

      if (session) {
        console.log('Session found:', session.user.email);
        const user = session.user;
        setUser({
          id: user.id,
          email: user.email || '',
          name: user.user_metadata?.name || user.email?.split('@')[0] || '',
          picture: user.user_metadata?.avatar_url,
        });
        api.setAuthToken(session.access_token);
      } else {
        console.log('No session found');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      console.log('Auth check complete');
      setIsLoading(false);
    }
  };

  const login = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          scopes: 'openid email profile https://www.googleapis.com/auth/gmail.readonly',
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      });

      if (error) throw error;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      // Clear local state immediately for responsive UI
      setUser(null);
      api.setAuthToken(null);

      // Sign out from Supabase
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error('Supabase signOut error:', error);
      }

      // Navigate after state is cleared
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Still navigate even if signOut fails
      router.push('/login');
    }
  };

  const getStatus = (): AuthStatus => {
    if (isLoading) return 'loading';
    if (user) return 'authenticated';
    return 'unauthenticated';
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    status: getStatus(),
    login,
    logout,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
