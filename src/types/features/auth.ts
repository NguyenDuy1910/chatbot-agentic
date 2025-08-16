export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  bio?: string;
  phone?: string;
  location?: string;
  timezone?: string;
  role: 'user' | 'admin';
  status: 'active' | 'inactive' | 'banned';
  createdAt: Date;
  lastActive: Date;
  totalChats: number;
  totalMessages: number;
  preferences: {
    theme: 'light' | 'dark' | 'system';
    language: string;
    notifications: {
      email: boolean;
      push: boolean;
      chat: boolean;
    };
    privacy: {
      showProfile: boolean;
      showActivity: boolean;
    };
  };
}

export interface AuthResponse {
  user: UserProfile;
  token: string;
  refreshToken: string;
  expiresIn: number;
}

export interface PasswordUpdate {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ProfileUpdate {
  name?: string;
  bio?: string;
  phone?: string;
  location?: string;
  timezone?: string;
  avatar?: File;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
}
