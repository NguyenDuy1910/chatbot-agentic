/**
 * API configuration - Updated to match REST API naming conventions
 * 
 * BREAKING CHANGES:
 * - auth.signup → auth.register
 * - auth.signin → auth.login  
 * - auth.signout → auth.logout
 * - auth.me now points to /api/v1/auth/me (was /api/v1/auth/user)
 * - auth.profile → auth.me/profile
 * - auth.password → auth.me/password
 * - All resource IDs use descriptive names (chat_id, user_id, etc.)
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
      register: '/api/v1/auth/register',
      login: '/api/v1/auth/login',
      logout: '/api/v1/auth/logout',
      me: '/api/v1/auth/me', // Current user endpoint
      profile: '/api/v1/auth/me/profile',
      password: '/api/v1/auth/me/password',
    },

    // Chat resource endpoints
    chats: {
      base: '/api/v1/chats',
      byId: (chat_id: string) => `/api/v1/chats/${chat_id}`,
      archive: (chat_id: string) => `/api/v1/chats/${chat_id}/archive`,
      pin: (chat_id: string) => `/api/v1/chats/${chat_id}/pin`,
      share: (chat_id: string) => `/api/v1/chats/${chat_id}/share`,
    },

    // Message resource endpoints
    messages: {
      base: '/api/v1/messages',
      byId: (message_id: string) => `/api/v1/messages/${message_id}`,
      byChatId: (chat_id: string) => `/api/v1/chats/${chat_id}/messages`,
    },

    // User resource endpoints
    users: {
      base: '/api/v1/users',
      byId: (user_id: string) => `/api/v1/users/${user_id}`,
      me: '/api/v1/users/me',
      meSettings: '/api/v1/users/me/settings',
      meGroups: '/api/v1/users/me/groups',
      mePermissions: '/api/v1/users/me/permissions',
      roleById: (user_id: string) => `/api/v1/users/${user_id}/role`,
    },

    // Connection resource endpoints
    connections: {
      base: '/api/v1/connections',
      byId: (connection_id: string) => `/api/v1/connections/${connection_id}`,
      test: '/api/v1/connections/test',
      testById: (connection_id: string) => `/api/v1/connections/${connection_id}/test`,
      templates: '/api/v1/connections/templates',
      stats: '/api/v1/connections/statistics',
      logs: (connection_id: string) => `/api/v1/connections/${connection_id}/logs`,
      healthCheck: (connection_id: string) => `/api/v1/connections/${connection_id}/health-check`,
    },

    // Knowledge resource endpoints
    knowledge: {
      base: '/api/v1/knowledge',
      byId: (knowledge_id: string) => `/api/v1/knowledge/${knowledge_id}`,
    },

    // File resource endpoints
    files: {
      base: '/api/v1/files',
      byId: (file_id: string) => `/api/v1/files/${file_id}`,
      upload: '/api/v1/files/upload',
      searchByHash: (file_hash: string) => `/api/v1/files/search/by-hash/${file_hash}`,
      searchByFilename: (filename: string) => `/api/v1/files/search/by-filename/${filename}`,
    },

    // Prompt resource endpoints
    prompts: {
      base: '/api/v1/prompts',
      byId: (prompt_id: string) => `/api/v1/prompts/${prompt_id}`,
      templates: '/api/v1/prompts/templates',
      use: (prompt_id: string) => `/api/v1/prompts/${prompt_id}/use`,
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
    register: () => apiConfig.endpoints.auth.register,
    login: () => apiConfig.endpoints.auth.login,
    logout: () => apiConfig.endpoints.auth.logout,
    me: () => apiConfig.endpoints.auth.me,
    profile: () => apiConfig.endpoints.auth.profile,
    password: () => apiConfig.endpoints.auth.password,
  },

  // Resource URLs with proper REST patterns
  chats: {
    list: () => apiConfig.endpoints.chats.base,
    create: () => apiConfig.endpoints.chats.base,
    get: (chat_id: string) => apiConfig.endpoints.chats.byId(chat_id),
    update: (chat_id: string) => apiConfig.endpoints.chats.byId(chat_id),
    delete: (chat_id: string) => apiConfig.endpoints.chats.byId(chat_id),
    archive: (chat_id: string) => apiConfig.endpoints.chats.archive(chat_id),
    pin: (chat_id: string) => apiConfig.endpoints.chats.pin(chat_id),
    share: (chat_id: string) => apiConfig.endpoints.chats.share(chat_id),
  },

  messages: {
    list: () => apiConfig.endpoints.messages.base,
    create: () => apiConfig.endpoints.messages.base,
    get: (message_id: string) => apiConfig.endpoints.messages.byId(message_id),
    update: (message_id: string) => apiConfig.endpoints.messages.byId(message_id),
    delete: (message_id: string) => apiConfig.endpoints.messages.byId(message_id),
    byChatId: (chat_id: string) => apiConfig.endpoints.messages.byChatId(chat_id),
  },

  users: {
    list: () => apiConfig.endpoints.users.base,
    create: () => apiConfig.endpoints.users.base,
    get: (user_id: string) => apiConfig.endpoints.users.byId(user_id),
    update: (user_id: string) => apiConfig.endpoints.users.byId(user_id),
    delete: (user_id: string) => apiConfig.endpoints.users.byId(user_id),
    me: () => apiConfig.endpoints.users.me,
    meSettings: () => apiConfig.endpoints.users.meSettings,
    meGroups: () => apiConfig.endpoints.users.meGroups,
    mePermissions: () => apiConfig.endpoints.users.mePermissions,
    updateRole: (user_id: string) => apiConfig.endpoints.users.roleById(user_id),
  },

  connections: {
    list: () => apiConfig.endpoints.connections.base,
    create: () => apiConfig.endpoints.connections.base,
    get: (connection_id: string) => apiConfig.endpoints.connections.byId(connection_id),
    update: (connection_id: string) => apiConfig.endpoints.connections.byId(connection_id),
    delete: (connection_id: string) => apiConfig.endpoints.connections.byId(connection_id),
    test: () => apiConfig.endpoints.connections.test,
    testById: (connection_id: string) => apiConfig.endpoints.connections.testById(connection_id),
    templates: () => apiConfig.endpoints.connections.templates,
    stats: () => apiConfig.endpoints.connections.stats,
    logs: (connection_id: string) => apiConfig.endpoints.connections.logs(connection_id),
    healthCheck: (connection_id: string) => apiConfig.endpoints.connections.healthCheck(connection_id),
  },

  files: {
    list: () => apiConfig.endpoints.files.base,
    create: () => apiConfig.endpoints.files.base,
    get: (file_id: string) => apiConfig.endpoints.files.byId(file_id),
    update: (file_id: string) => apiConfig.endpoints.files.byId(file_id),
    delete: (file_id: string) => apiConfig.endpoints.files.byId(file_id),
    upload: () => apiConfig.endpoints.files.upload,
    searchByHash: (file_hash: string) => apiConfig.endpoints.files.searchByHash(file_hash),
    searchByFilename: (filename: string) => apiConfig.endpoints.files.searchByFilename(filename),
  },

  prompts: {
    list: () => apiConfig.endpoints.prompts.base,
    create: () => apiConfig.endpoints.prompts.base,
    get: (prompt_id: string) => apiConfig.endpoints.prompts.byId(prompt_id),
    update: (prompt_id: string) => apiConfig.endpoints.prompts.byId(prompt_id),
    delete: (prompt_id: string) => apiConfig.endpoints.prompts.byId(prompt_id),
    templates: () => apiConfig.endpoints.prompts.templates,
    use: (prompt_id: string) => apiConfig.endpoints.prompts.use(prompt_id),
  },
};

// Backward compatibility aliases (DEPRECATED - use the new names above)
export const legacyApiUrls = {
  auth: {
    signup: () => apiConfig.endpoints.auth.register, // Use auth.register instead
    signin: () => apiConfig.endpoints.auth.login,    // Use auth.login instead
    signout: () => apiConfig.endpoints.auth.logout,  // Use auth.logout instead
  },
};
