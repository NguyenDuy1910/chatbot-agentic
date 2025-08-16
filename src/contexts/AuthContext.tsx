import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthState, LoginCredentials, RegisterData, PasswordUpdate, ProfileUpdate } from '@/types/features/auth';
import { authAPI } from '@/lib/authAPI';

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
      if (authAPI.isAuthenticated()) {
        const user = await authAPI.getCurrentUser();
        setAuthState({
          isAuthenticated: true,
          user,
          loading: false,
          error: null
        });
      } else {
        setAuthState({
          isAuthenticated: false,
          user: null,
          loading: false,
          error: null
        });
      }
    } catch (error) {
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: error instanceof Error ? error.message : 'Authentication failed'
      });
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      setAuthState(prev => ({ ...prev, loading: true, error: null }));
      
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
