import {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  UserProfile,
  PasswordUpdate,
  ProfileUpdate,
  SigninForm,
  SignupForm,
  SigninResponse,
  UserResponse,
  UpdatePasswordForm,
  UpdateProfileForm
} from '@/types/features/auth';
import { api } from './api';
import { apiConfig } from '@/config/api';

class AuthAPI {
  private token: string | null = localStorage.getItem('authToken');

  // Set auth token
  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
  }

  // Convert frontend types to backend types
  private convertToSigninForm(credentials: LoginCredentials): SigninForm {
    return {
      email: credentials.email,
      password: credentials.password,
    };
  }

  private convertToSignupForm(data: RegisterData): SignupForm {
    return {
      name: data.name,
      email: data.email,
      password: data.password,
      profile_image_url: data.profile_image_url || '',
    };
  }

  // Convert backend response to frontend types
  private convertToUserProfile(userResponse: UserResponse): UserProfile {
    return {
      id: userResponse.id,
      name: userResponse.name,
      email: userResponse.email,
      avatar: userResponse.profile_image_url,
      role: userResponse.role as 'user' | 'admin' | 'pending',
      status: 'active',
      createdAt: new Date(),
      lastActive: new Date(),
      totalChats: 0,
      totalMessages: 0,
      preferences: {
        theme: 'system',
        language: 'en',
        notifications: {
          email: true,
          push: false,
          chat: true
        },
        privacy: {
          showProfile: true,
          showActivity: false
        }
      }
    };
  }

  // Login user
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const signinForm = this.convertToSigninForm(credentials);
      const response = await api.post<SigninResponse>(
        apiConfig.endpoints.auth.login,
        signinForm
      );

      // Convert backend response to frontend format
      const user = this.convertToUserProfile(response);

      const authResponse: AuthResponse = {
        user,
        token: response.token,
        refreshToken: undefined, // Backend doesn't provide refresh token yet
        expiresIn: 86400 // 24 hours in seconds
      };

      this.setToken(response.token);
      localStorage.setItem('user', JSON.stringify(user));

      return authResponse;
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error(error instanceof Error ? error.message : 'Login failed');
    }
  }

  // Register user
  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      if (data.password !== data.confirmPassword) {
        throw new Error('Passwords do not match');
      }

      const signupForm = this.convertToSignupForm(data);
      const response = await api.post<SigninResponse>(
        apiConfig.endpoints.auth.register,
        signupForm
      );

      // Convert backend response to frontend format
      const user = this.convertToUserProfile(response);

      const authResponse: AuthResponse = {
        user,
        token: response.token,
        refreshToken: undefined,
        expiresIn: 86400 // 24 hours in seconds
      };

      this.setToken(response.token);
      localStorage.setItem('user', JSON.stringify(user));

      return authResponse;
    } catch (error) {
      console.error('Registration failed:', error);
      throw new Error(error instanceof Error ? error.message : 'Registration failed');
    }
  }

  // Logout user
  async logout(): Promise<void> {
    try {
      // Call backend signout endpoint
      await api.post(apiConfig.endpoints.auth.logout);
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with local cleanup even if API call fails
    } finally {
      this.setToken(null);
    }
  }

  // Get current user
  async getCurrentUser(): Promise<UserProfile> {
    if (!this.token) {
      throw new Error('No authentication token');
    }

    try {
      // Try to get user from backend first
      const response = await api.get<UserResponse>(apiConfig.endpoints.auth.me);
      const user = this.convertToUserProfile(response);

      // Update local storage
      localStorage.setItem('user', JSON.stringify(user));

      return user;
    } catch (error) {
      // Fallback to local storage
      const userData = localStorage.getItem('user');
      if (userData) {
        return JSON.parse(userData);
      }

      throw new Error('User not found');
    }
  }

  // Update user profile
  async updateProfile(updates: ProfileUpdate): Promise<UserProfile> {
    if (!this.token) {
      throw new Error('Not authenticated');
    }

    try {
      // Handle avatar upload if provided
      let profile_image_url = '';
      if (updates.avatar) {
        // TODO: Implement file upload to backend
        profile_image_url = URL.createObjectURL(updates.avatar);
      }

      const updateForm: UpdateProfileForm = {
        name: updates.name || '',
        profile_image_url: profile_image_url
      };

      const response = await api.put<UserResponse>(
        apiConfig.endpoints.auth.profile,
        updateForm
      );

      const updatedUser = this.convertToUserProfile(response);

      // Update local storage
      localStorage.setItem('user', JSON.stringify(updatedUser));

      return updatedUser;
    } catch (error) {
      console.error('Profile update failed:', error);
      throw new Error(error instanceof Error ? error.message : 'Profile update failed');
    }
  }

  // Update password
  async updatePassword(passwordData: PasswordUpdate): Promise<void> {
    if (!this.token) {
      throw new Error('Not authenticated');
    }

    try {
      if (passwordData.newPassword !== passwordData.confirmPassword) {
        throw new Error('New passwords do not match');
      }

      const updateForm: UpdatePasswordForm = {
        password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      };

      await api.put(apiConfig.endpoints.auth.password, updateForm);
    } catch (error) {
      console.error('Password update failed:', error);
      throw new Error(error instanceof Error ? error.message : 'Password update failed');
    }
  }

  // Refresh token
  async refreshToken(): Promise<AuthResponse> {
    try {
      // For now, just get current user since backend doesn't have refresh endpoint yet
      const user = await this.getCurrentUser();

      return {
        user,
        token: this.token || '',
        refreshToken: undefined,
        expiresIn: 86400
      };
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw new Error('Token refresh failed');
    }
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.token;
  }
}

export const authAPI = new AuthAPI();
