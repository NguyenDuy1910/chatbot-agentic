/**
 * API configuration
 */
import { env } from './env';

export const apiConfig = {
  baseURL: env.API_BASE_URL,
  timeout: env.API_TIMEOUT,

  // API prefix to match backend
  apiPrefix: '/api/v1',

  // Endpoints - REST API naming convention
  endpoints: {
    // Authentication endpoints
    auth: {
      base: '/api/v1/auth',
      signup: '/api/v1/auth/signup',
      signin: '/api/v1/auth/signin',
      signout: '/api/v1/auth/signout',
      me: '/api/v1/auth/user', // Current user endpoint
      profile: '/api/v1/auth/profile',
      password: '/api/v1/auth/password',
    },

    // Chat resource endpoints
    chats: {
      base: '/api/v1/chats',
      byId: (id: string) => `/api/v1/chats/${id}`,
      archive: (id: string) => `/api/v1/chats/${id}/archive`,
      pin: (id: string) => `/api/v1/chats/${id}/pin`,
    },

    // Message resource endpoints
    messages: {
      base: '/api/v1/messages',
      byId: (id: string) => `/api/v1/messages/${id}`,
      byChatId: (chatId: string) => `/api/v1/chats/${chatId}/messages`,
    },

    // User resource endpoints
    users: {
      base: '/api/v1/users',
      byId: (id: string) => `/api/v1/users/${id}`,
    },

    // Connection resource endpoints
    connections: {
      base: '/api/v1/connections',
      byId: (id: string) => `/api/v1/connections/${id}`,
      test: '/api/v1/connections/test',
      testById: (id: string) => `/api/v1/connections/${id}/test`,
      templates: '/api/v1/connections/templates',
      stats: '/api/v1/connections/stats',
      logs: (id: string) => `/api/v1/connections/${id}/logs`,
    },

    // Knowledge resource endpoints
    knowledge: {
      base: '/api/v1/knowledge',
      byId: (id: string) => `/api/v1/knowledge/${id}`,
    },

    // File resource endpoints
    files: {
      base: '/api/v1/files',
      byId: (id: string) => `/api/v1/files/${id}`,
      upload: '/api/v1/files/upload',
    },

    // Prompt resource endpoints
    prompts: {
      base: '/api/v1/prompts',
      byId: (id: string) => `/api/v1/prompts/${id}`,
      templates: '/api/v1/prompts/templates',
      use: (id: string) => `/api/v1/prompts/${id}/use`,
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

// Helper functions for building API URLs
export const buildApiUrl = {
  // Authentication URLs
  auth: {
    signup: () => apiConfig.endpoints.auth.signup,
    signin: () => apiConfig.endpoints.auth.signin,
    signout: () => apiConfig.endpoints.auth.signout,
    me: () => apiConfig.endpoints.auth.me,
    profile: () => apiConfig.endpoints.auth.profile,
    password: () => apiConfig.endpoints.auth.password,
  },

  // Resource URLs with proper REST patterns
  chats: {
    list: () => apiConfig.endpoints.chats.base,
    create: () => apiConfig.endpoints.chats.base,
    get: (id: string) => apiConfig.endpoints.chats.byId(id),
    update: (id: string) => apiConfig.endpoints.chats.byId(id),
    delete: (id: string) => apiConfig.endpoints.chats.byId(id),
    archive: (id: string) => apiConfig.endpoints.chats.archive(id),
    pin: (id: string) => apiConfig.endpoints.chats.pin(id),
  },

  messages: {
    list: () => apiConfig.endpoints.messages.base,
    create: () => apiConfig.endpoints.messages.base,
    get: (id: string) => apiConfig.endpoints.messages.byId(id),
    update: (id: string) => apiConfig.endpoints.messages.byId(id),
    delete: (id: string) => apiConfig.endpoints.messages.byId(id),
    byChatId: (chatId: string) => apiConfig.endpoints.messages.byChatId(chatId),
  },

  connections: {
    list: () => apiConfig.endpoints.connections.base,
    create: () => apiConfig.endpoints.connections.base,
    get: (id: string) => apiConfig.endpoints.connections.byId(id),
    update: (id: string) => apiConfig.endpoints.connections.byId(id),
    delete: (id: string) => apiConfig.endpoints.connections.byId(id),
    test: () => apiConfig.endpoints.connections.test,
    testById: (id: string) => apiConfig.endpoints.connections.testById(id),
    templates: () => apiConfig.endpoints.connections.templates,
    stats: () => apiConfig.endpoints.connections.stats,
    logs: (id: string) => apiConfig.endpoints.connections.logs(id),
  },

  prompts: {
    list: () => apiConfig.endpoints.prompts.base,
    create: () => apiConfig.endpoints.prompts.base,
    get: (id: string) => apiConfig.endpoints.prompts.byId(id),
    update: (id: string) => apiConfig.endpoints.prompts.byId(id),
    delete: (id: string) => apiConfig.endpoints.prompts.byId(id),
    templates: () => apiConfig.endpoints.prompts.templates,
    use: (id: string) => apiConfig.endpoints.prompts.use(id),
  },
};
