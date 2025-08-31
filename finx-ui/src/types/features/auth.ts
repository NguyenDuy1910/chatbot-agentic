// Backend-compatible auth types
export interface SigninForm {
  email: string;
  password: string;
}

export interface SignupForm {
  name: string;
  email: string;
  password: string;
  profile_image_url?: string;
}

export interface UpdatePasswordForm {
  password: string;
  new_password: string;
}

export interface UpdateProfileForm {
  profile_image_url: string;
  name: string;
}

// Backend response types
export interface UserResponse {
  id: string;
  email: string;
  name: string;
  role: string;
  profile_image_url: string;
}

export interface SigninResponse extends UserResponse {
  token: string;
  token_type: string;
}

// Frontend-compatible types (for backward compatibility)
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
  profile_image_url?: string;
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
  role: 'user' | 'admin' | 'pending';
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
  refreshToken?: string;
  expiresIn?: number;
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
