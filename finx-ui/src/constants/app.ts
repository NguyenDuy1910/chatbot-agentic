/**
 * Application constants
 */

// App metadata
export const APP_INFO = {
  name: 'Vikki ChatBot',
  version: '1.0.0',
  description: 'Modern chatbot frontend - Vikki ChatBot',
  author: 'Vikki Bank AI Team',
} as const;

// Local storage keys
export const STORAGE_KEYS = {
  theme: 'vikki_theme',
  authToken: 'vikki_auth_token',
  userPreferences: 'vikki_user_preferences',
  chatHistory: 'vikki_chat_history',
  connectionSettings: 'vikki_connection_settings',
} as const;

// Session storage keys
export const SESSION_KEYS = {
  currentConversation: 'vikki_current_conversation',
  tempData: 'vikki_temp_data',
} as const;

// Default values
export const DEFAULTS = {
  pagination: {
    page: 1,
    limit: 20,
  },
  chat: {
    maxMessages: 100,
    typingDelay: 1000,
  },
  connection: {
    timeout: 10000,
    retryAttempts: 3,
  },
} as const;

// Validation rules
export const VALIDATION = {
  password: {
    minLength: 8,
    maxLength: 128,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
  },
  username: {
    minLength: 3,
    maxLength: 50,
    pattern: /^[a-zA-Z0-9_-]+$/,
  },
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
} as const;
