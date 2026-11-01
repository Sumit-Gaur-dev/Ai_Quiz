import { createClient } from '@supabase/supabase-js';
import config from '../config/index.js';

// In-memory profile store for local development before Supabase credentials are provided
const devProfiles = new Map();

const createDevSupabaseClient = (accessToken = null) => {
  return {
    auth: {
      async getUser(token) {
        if (!token || token.includes('invalid') || token.includes('expired')) {
          return { data: { user: null }, error: { message: 'Invalid or expired token' } };
        }
        const userId = token.startsWith('dev-token-')
          ? token.replace('dev-token-', '')
          : 'dev-user';

        return {
          data: {
            user: {
              id: userId,
              email: `${userId}@example.com`,
              user_metadata: { display_name: 'Dev User' },
              app_metadata: { provider: 'email' },
            },
          },
          error: null,
        };
      },
    },
    from(table) {
      if (table === 'profiles') {
        return {
          select(_fields) {
            return {
              eq(field, value) {
                return {
                  async maybeSingle() {
                    const profile = devProfiles.get(value) || {
                      id: value,
                      display_name: 'Dev User',
                      created_at: new Date().toISOString(),
                      updated_at: new Date().toISOString(),
                    };
                    return { data: profile, error: null };
                  },
                };
              },
            };
          },
          update(updates) {
            return {
              eq(field, value) {
                return {
                  select() {
                    return {
                      async single() {
                        const existing = devProfiles.get(value) || {
                          id: value,
                          created_at: new Date().toISOString(),
                        };
                        const updated = {
                          ...existing,
                          ...updates,
                          id: value,
                          updated_at: new Date().toISOString(),
                        };
                        devProfiles.set(value, updated);
                        return { data: updated, error: null };
                      },
                    };
                  },
                };
              },
            };
          },
        };
      }
      throw new Error(`Table ${table} not supported in local dev fallback mode`);
    },
  };
};

/**
 * Creates or returns a Supabase client.
 * If Supabase environment variables are present, returns real Supabase client.
 * Otherwise provides a seamless local development fallback.
 *
 * @param {string|null} accessToken
 * @returns {import('@supabase/supabase-js').SupabaseClient}
 */
export const getSupabaseClient = (accessToken = null) => {
  const isConfigured = Boolean(
    config.supabaseUrl &&
    config.supabaseAnonKey &&
    !config.supabaseUrl.includes('placeholder')
  );

  if (!isConfigured) {
    return createDevSupabaseClient(accessToken);
  }

  const options = {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  };

  if (accessToken) {
    options.global = {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    };
  }

  return createClient(config.supabaseUrl, config.supabaseAnonKey, options);
};

/**
 * Creates a privileged Supabase client using the service role key.
 * Used strictly for server-side maintenance or admin operations.
 * Never expose to browser.
 *
 * @returns {import('@supabase/supabase-js').SupabaseClient}
 */
export const getSupabaseAdminClient = () => {
  if (!config.supabaseUrl || !config.supabaseServiceRoleKey) {
    throw new Error('Supabase URL or Service Role Key is missing in environment variables');
  }

  return createClient(config.supabaseUrl, config.supabaseServiceRoleKey, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });
};
