/**
 * Environment configuration
 */

export const env = {
  // App environment
  NODE_ENV: import.meta.env.NODE_ENV || 'development',
  
  // API configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  API_TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  
  // Authentication
  JWT_SECRET: import.meta.env.VITE_JWT_SECRET,
  AUTH_COOKIE_NAME: import.meta.env.VITE_AUTH_COOKIE_NAME || 'vikki_auth_token',
  
  // Database
  DB_CONNECTION_TIMEOUT: parseInt(import.meta.env.VITE_DB_CONNECTION_TIMEOUT || '10000'),
  
  // Features flags
  ENABLE_ADMIN_FEATURES: import.meta.env.VITE_ENABLE_ADMIN_FEATURES === 'true',
  ENABLE_DEBUG_MODE: import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true',

  // UI Configuration
  DEFAULT_THEME: import.meta.env.VITE_DEFAULT_THEME || 'light',
  ENABLE_DARK_MODE: import.meta.env.VITE_ENABLE_DARK_MODE !== 'false',

  // Development Authentication
  ENABLE_MOCK_AUTH: import.meta.env.VITE_ENABLE_MOCK_AUTH === 'true',
  MOCK_USER_NAME: import.meta.env.VITE_MOCK_USER_NAME || 'Development User',
  MOCK_USER_EMAIL: import.meta.env.VITE_MOCK_USER_EMAIL || 'dev@vikki.vn',
  MOCK_USER_ROLE: import.meta.env.VITE_MOCK_USER_ROLE || 'admin',
} as const;

// Validation
export const validateEnv = () => {
  const required = ['API_BASE_URL'];
  const missing = required.filter(key => !env[key as keyof typeof env]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
};

// Development helpers
export const isDevelopment = env.NODE_ENV === 'development';
export const isProduction = env.NODE_ENV === 'production';
export const isTest = env.NODE_ENV === 'test';
