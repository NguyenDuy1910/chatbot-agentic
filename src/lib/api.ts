import { apiConfig } from '@/config/api';
import { env } from '@/config/env';

/**
 * API utility functions for making HTTP requests
 */

// Get auth token from localStorage or cookie
const getAuthToken = (): string | null => {
  // Try localStorage first
  const token = localStorage.getItem('authToken');
  if (token) return token;

  // Try cookie as fallback
  const cookies = document.cookie.split(';');
  const tokenCookie = cookies.find(cookie =>
    cookie.trim().startsWith(`${env.AUTH_COOKIE_NAME}=`)
  );

  if (tokenCookie) {
    return tokenCookie.split('=')[1];
  }

  return null;
};

// Create headers with authentication
const createHeaders = (additionalHeaders: Record<string, string> = {}): HeadersInit => {
  const headers: Record<string, string> = {
    ...apiConfig.defaultHeaders,
    ...additionalHeaders,
  };

  const token = getAuthToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
};

// Generic API request function
export const apiRequest = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${apiConfig.baseURL}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: createHeaders(options.headers as Record<string, string>),
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return response.text() as unknown as T;
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
};

// HTTP method helpers
export const api = {
  get: <T = any>(endpoint: string, options?: RequestInit): Promise<T> =>
    apiRequest<T>(endpoint, { ...options, method: 'GET' }),

  post: <T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T = any>(endpoint: string, options?: RequestInit): Promise<T> =>
    apiRequest<T>(endpoint, { ...options, method: 'DELETE' }),
};

// Note: Legacy chatAPI has been moved to chatAPI.ts
// Import { chatAPI } from './chatAPI' for chat functionality
