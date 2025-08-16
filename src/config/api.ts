/**
 * API configuration
 */
import { env } from './env';

export const apiConfig = {
  baseURL: env.API_BASE_URL,
  timeout: env.API_TIMEOUT,
  
  // Endpoints
  endpoints: {
    auth: {
      login: '/auth/login',
      logout: '/auth/logout',
      refresh: '/auth/refresh',
      profile: '/auth/profile',
    },
    chat: {
      messages: '/chat/messages',
      conversations: '/chat/conversations',
      stream: '/chat/stream',
    },
    admin: {
      users: '/admin/users',
      settings: '/admin/settings',
      analytics: '/admin/analytics',
    },
    connections: {
      list: '/connections',
      create: '/connections',
      test: '/connections/test',
      delete: '/connections',
    },
    database: {
      query: '/database/query',
      schema: '/database/schema',
      tables: '/database/tables',
    },
    prompts: {
      list: '/prompts',
      create: '/prompts',
      update: '/prompts',
      delete: '/prompts',
    },
  },
  
  // Headers
  defaultHeaders: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Retry configuration
  retry: {
    attempts: 3,
    delay: 1000,
    backoff: 2,
  },
} as const;
