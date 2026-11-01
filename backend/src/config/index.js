import dotenv from 'dotenv';

dotenv.config();

const config = {
  nodeEnv: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 5000,
  frontendOrigin: process.env.FRONTEND_ORIGIN || 'http://localhost:3000',
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY,
  supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY,
  ragServiceUrl: process.env.RAG_SERVICE_URL || 'http://localhost:8000',
  internalServiceToken: process.env.INTERNAL_SERVICE_TOKEN,
  requestTimeoutMs: parseInt(process.env.REQUEST_TIMEOUT_MS, 10) || 60000,
};

export default config;

