'use client';

import { createContext, useContext, useEffect, useState, useMemo } from 'react';
import { createClient } from '@/lib/supabase/client';

const AuthContext = createContext({
  user: null,
  session: null,
  loading: true,
  isDevMode: false,
  signIn: async () => {},
  signUp: async () => {},
  signOut: async () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  const isConfigured = useMemo(() => {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    return Boolean(
      url &&
      key &&
      url.trim() !== '' &&
      !url.includes('placeholder.supabase.co')
    );
  }, []);

  useEffect(() => {
    if (isConfigured) {
      const supabase = createClient();

      // Check initial active session from Supabase
      supabase.auth.getSession().then(({ data: { session } }) => {
        setSession(session);
        setUser(session?.user ?? null);
        setLoading(false);
      });

      // Listen to changes in auth state
      const {
        data: { subscription },
      } = supabase.auth.onAuthStateChange((_event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        setLoading(false);
      });

      return () => {
        subscription?.unsubscribe();
      };
    } else {
      // Local development mode: restore session from localStorage if available
      try {
        const stored = typeof window !== 'undefined' ? localStorage.getItem('aiquiz_dev_session') : null;
        if (stored) {
          const parsed = JSON.parse(stored);
          setUser(parsed.user ?? null);
          setSession(parsed);
        }
      } catch (e) {
        console.warn('Failed to parse dev session:', e);
      } finally {
        setLoading(false);
      }
    }
  }, [isConfigured]);

  const signIn = async (email, password) => {
    if (isConfigured) {
      const supabase = createClient();
      return await supabase.auth.signInWithPassword({
        email,
        password,
      });
    }

    // Local Development Fallback
    const cleanEmail = email.trim().toLowerCase();
    const userId = 'dev-' + Math.abs(cleanEmail.split('').reduce((acc, c) => (acc * 31 + c.charCodeAt(0)) | 0, 0)).toString(16);

    const devUser = {
      id: userId,
      email: cleanEmail,
      user_metadata: {
        display_name: cleanEmail.split('@')[0],
      },
      app_metadata: { provider: 'email' },
    };

    const devSession = {
      access_token: 'dev-token-' + userId,
      token_type: 'bearer',
      user: devUser,
      expires_in: 3600,
    };

    if (typeof window !== 'undefined') {
      localStorage.setItem('aiquiz_dev_session', JSON.stringify(devSession));
    }

    setUser(devUser);
    setSession(devSession);
    return { data: { user: devUser, session: devSession }, error: null };
  };

  const signUp = async (email, password, displayName) => {
    if (isConfigured) {
      const supabase = createClient();
      return await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            display_name: displayName,
          },
        },
      });
    }

    // Local Development Fallback
    const cleanEmail = email.trim().toLowerCase();
    const cleanName = displayName.trim();
    const userId = 'dev-' + Math.abs(cleanEmail.split('').reduce((acc, c) => (acc * 31 + c.charCodeAt(0)) | 0, 0)).toString(16);

    const devUser = {
      id: userId,
      email: cleanEmail,
      user_metadata: {
        display_name: cleanName || cleanEmail.split('@')[0],
      },
      app_metadata: { provider: 'email' },
    };

    const devSession = {
      access_token: 'dev-token-' + userId,
      token_type: 'bearer',
      user: devUser,
      expires_in: 3600,
    };

    if (typeof window !== 'undefined') {
      localStorage.setItem('aiquiz_dev_session', JSON.stringify(devSession));
    }

    setUser(devUser);
    setSession(devSession);
    return { data: { user: devUser, session: devSession }, error: null };
  };

  const signOut = async () => {
    if (isConfigured) {
      const supabase = createClient();
      return await supabase.auth.signOut();
    }

    if (typeof window !== 'undefined') {
      localStorage.removeItem('aiquiz_dev_session');
    }
    setUser(null);
    setSession(null);
    return { error: null };
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        loading,
        isDevMode: !isConfigured,
        signIn,
        signUp,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
