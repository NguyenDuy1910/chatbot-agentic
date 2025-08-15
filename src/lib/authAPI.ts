import { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  UserProfile, 
  PasswordUpdate, 
  ProfileUpdate 
} from '@/types/auth';

// Mock API - replace with actual API endpoints
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

class AuthAPI {
  private token: string | null = localStorage.getItem('authToken');

  // Set auth token
  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }

  // Login user
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    await delay(1000); // Simulate API delay
    
    // Mock login logic - replace with actual API call
    if (credentials.email === 'demo@vikki.com' && credentials.password === 'demo123') {
      const mockUser: UserProfile = {
        id: '1',
        name: 'Demo User',
        email: 'demo@vikki.com',
        avatar: undefined,
        bio: 'Welcome to Vikki ChatBot!',
        role: 'user',
        status: 'active',
        createdAt: new Date('2024-01-01'),
        lastActive: new Date(),
        totalChats: 15,
        totalMessages: 150,
        preferences: {
          theme: 'system',
          language: 'en',
          notifications: {
            email: true,
            push: true,
            chat: true
          },
          privacy: {
            showProfile: true,
            showActivity: false
          }
        }
      };

      const authResponse: AuthResponse = {
        user: mockUser,
        token: 'mock-jwt-token-123',
        refreshToken: 'mock-refresh-token-456',
        expiresIn: 3600
      };

      this.setToken(authResponse.token);
      return authResponse;
    }

    throw new Error('Invalid credentials');
  }

  // Register user
  async register(data: RegisterData): Promise<AuthResponse> {
    await delay(1500); // Simulate API delay
    
    if (data.password !== data.confirmPassword) {
      throw new Error('Passwords do not match');
    }

    // Mock registration - replace with actual API call
    const mockUser: UserProfile = {
      id: Math.random().toString(36).substr(2, 9),
      name: data.name,
      email: data.email,
      role: 'user',
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

    const authResponse: AuthResponse = {
      user: mockUser,
      token: 'mock-jwt-token-new-user',
      refreshToken: 'mock-refresh-token-new',
      expiresIn: 3600
    };

    this.setToken(authResponse.token);
    return authResponse;
  }

  // Logout user
  async logout(): Promise<void> {
    await delay(500);
    this.setToken(null);
    localStorage.removeItem('user');
  }

  // Get current user
  async getCurrentUser(): Promise<UserProfile> {
    if (!this.token) {
      throw new Error('No authentication token');
    }

    await delay(800);
    
    // Mock user data - replace with actual API call
    const userData = localStorage.getItem('user');
    if (userData) {
      return JSON.parse(userData);
    }

    throw new Error('User not found');
  }

  // Update user profile
  async updateProfile(updates: ProfileUpdate): Promise<UserProfile> {
    if (!this.token) {
      throw new Error('Not authenticated');
    }

    await delay(1200);
    
    // Mock update - replace with actual API call
    const currentUser = await this.getCurrentUser();
    
    // Handle avatar upload if provided
    let avatarUrl = currentUser.avatar;
    if (updates.avatar) {
      // Mock avatar upload - replace with actual file upload
      avatarUrl = URL.createObjectURL(updates.avatar);
    }

    const updatedUser: UserProfile = {
      ...currentUser,
      ...updates,
      avatar: avatarUrl,
      lastActive: new Date()
    };

    // Remove the avatar file from updates since we've processed it
    const { avatar, ...userUpdates } = updates;
    Object.assign(updatedUser, userUpdates);

    localStorage.setItem('user', JSON.stringify(updatedUser));
    return updatedUser;
  }

  // Update password
  async updatePassword(passwordData: PasswordUpdate): Promise<void> {
    if (!this.token) {
      throw new Error('Not authenticated');
    }

    await delay(1000);
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      throw new Error('New passwords do not match');
    }

    // Mock password update - replace with actual API call
    // In real implementation, verify currentPassword against stored hash
    if (passwordData.currentPassword !== 'demo123') {
      throw new Error('Current password is incorrect');
    }

    // Password updated successfully
  }

  // Refresh token
  async refreshToken(): Promise<AuthResponse> {
    await delay(500);
    
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    // Mock token refresh - replace with actual API call
    const currentUser = await this.getCurrentUser();
    
    return {
      user: currentUser,
      token: 'new-mock-jwt-token',
      refreshToken: 'new-mock-refresh-token',
      expiresIn: 3600
    };
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.token;
  }
}

export const authAPI = new AuthAPI();
