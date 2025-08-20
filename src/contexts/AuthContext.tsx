import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthState, LoginCredentials, RegisterData, PasswordUpdate, ProfileUpdate } from '@/types/features/auth';
import { authAPI } from '@/lib/authAPI';
import { env } from '@/config/env';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (updates: ProfileUpdate) => Promise<void>;
  updatePassword: (passwordData: PasswordUpdate) => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    loading: true,
    error: null
  });

  // Initialize auth state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      console.log('🔍 Auth Debug:', {
        ENABLE_MOCK_AUTH: env.ENABLE_MOCK_AUTH,
        NODE_ENV: env.NODE_ENV,
        shouldUseMock: env.ENABLE_MOCK_AUTH
      });

      // Development bypass - auto login with mock user
      if (env.ENABLE_MOCK_AUTH) {
        const mockUser = {
          id: 'dev-user-1',
          name: env.MOCK_USER_NAME,
          email: env.MOCK_USER_EMAIL,
          role: env.MOCK_USER_ROLE as 'admin' | 'user',
          avatar: '',
          createdAt: new Date(),
          updatedAt: new Date(),
          profile_image_url: '',
          status: 'active' as const,
          lastActive: new Date(),
          totalChats: 0,
          totalMessages: 0,
          preferences: {
            theme: 'light' as const,
            language: 'en',
            notifications: {
              email: true,
              push: true,
              chat: true
            },
            privacy: {
              showProfile: true,
              showActivity: true
            }
          }
        };

        console.log('🚀 Development Mode: Auto-login with mock user:', mockUser);

        setAuthState({
          isAuthenticated: true,
          user: mockUser,
          loading: false,
          error: null
        });
        return;
      }

      // Real API mode - clear any mock data first
      console.log('🔓 Real API mode - clearing any existing auth data');

      // Clear localStorage and tokens to start fresh
      localStorage.removeItem('user');
      authAPI.setToken(null);

      // Start with unauthenticated state
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null
      });

      console.log('✅ Auth initialized - ready for login');

      // If no stored user but have token, try to get user from API
      if (authAPI.isAuthenticated()) {
        try {
          console.log('🔍 Token exists, fetching user from API...');
          const user = await authAPI.getCurrentUser();
          localStorage.setItem('user', JSON.stringify(user));
          setAuthState({
            isAuthenticated: true,
            user,
            loading: false,
            error: null
          });
        } catch (apiError) {
          // API failed but token exists - clear token and show login
          console.warn('Token exists but API failed, clearing auth:', apiError);
          authAPI.setToken(null);
          localStorage.removeItem('user');
          setAuthState({
            isAuthenticated: false,
            user: null,
            loading: false,
            error: null
          });
        }
      } else {
        // No token, show login
        console.log('🔓 No token found, showing login');
        setAuthState({
          isAuthenticated: false,
          user: null,
          loading: false,
          error: null
        });
      }
    } catch (error) {
      console.error('Auth initialization failed:', error);
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null // Don't show error on init, just go to login
      });
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));

      // Use real API login

      // Real API login (fallback)
      const response = await authAPI.login(credentials);

      // Store user data in localStorage for persistence
      localStorage.setItem('user', JSON.stringify(response.user));

      setAuthState({
        isAuthenticated: true,
        user: response.user,
        loading: false,
        error: null
      });
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      }));
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await authAPI.register(data);
      
      // Store user data in localStorage for persistence
      localStorage.setItem('user', JSON.stringify(response.user));
      
      setAuthState({
        isAuthenticated: true,
        user: response.user,
        loading: false,
        error: null
      });
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Registration failed'
      }));
      throw error;
    }
  };

  const logout = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));
      
      await authAPI.logout();
      
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null
      });
    } catch (error) {
      // Even if logout fails on server, clear local state
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null
      });
    }
  };

  const updateProfile = async (updates: ProfileUpdate) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      const updatedUser = await authAPI.updateProfile(updates);
      
      setAuthState(prev => ({
        ...prev,
        user: updatedUser,
        loading: false,
        error: null
      }));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Profile update failed'
      }));
      throw error;
    }
  };

  const updatePassword = async (passwordData: PasswordUpdate) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
      await authAPI.updatePassword(passwordData);
      
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: null
      }));
    } catch (error) {
      setAuthState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Password update failed'
      }));
      throw error;
    }
  };

  const refreshAuth = async () => {
    try {
      setAuthState(prev => ({ ...prev, loading: true }));
      
      const response = await authAPI.refreshToken();
      
      setAuthState({
        isAuthenticated: true,
        user: response.user,
        loading: false,
        error: null
      });
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: error instanceof Error ? error.message : 'Token refresh failed'
      });
    }
  };

  const value: AuthContextType = {
    ...authState,
    login,
    register,
    logout,
    updateProfile,
    updatePassword,
    refreshAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
