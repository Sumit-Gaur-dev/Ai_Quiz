import { getSupabaseClient } from '../services/supabase.js';

/**
 * Middleware to authenticate requests using a Supabase access token.
 * Verifies the JWT via Supabase Auth and derives user ID and claims.
 */
export const requireAuth = async (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      error: {
        code: 'UNAUTHORIZED',
        message: 'Authorization header with Bearer token is required',
      },
    });
  }

  const token = authHeader.split(' ')[1]?.trim();

  if (!token) {
    return res.status(401).json({
      error: {
        code: 'UNAUTHORIZED',
        message: 'Token not provided in Authorization header',
      },
    });
  }

  try {
    const supabase = getSupabaseClient(token);
    const { data, error } = await supabase.auth.getUser(token);

    if (error || !data?.user) {
      return res.status(401).json({
        error: {
          code: 'UNAUTHORIZED',
          message: error?.message || 'Invalid or expired token',
        },
      });
    }

    // Derive user ID and claims ONLY from the verified token
    req.user = {
      id: data.user.id,
      email: data.user.email,
      userMetadata: data.user.user_metadata || {},
      appMetadata: data.user.app_metadata || {},
    };
    req.token = token;
    req.supabase = supabase;

    next();
  } catch (err) {
    console.error('Auth verification error:', err.message);
    return res.status(500).json({
      error: {
        code: 'AUTH_SERVICE_ERROR',
        message: 'Unable to verify authentication token at this time',
      },
    });
  }
};

