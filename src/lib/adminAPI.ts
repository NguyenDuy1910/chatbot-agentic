import { User, ChatStatistics, SystemSettings, AdminDashboardData } from '@/types/features/admin';

// Mock data for demonstration
const mockUsers: User[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    avatar: '',
    role: 'user',
    status: 'active',
    createdAt: new Date('2024-01-15'),
    lastActive: new Date(),
    totalChats: 45,
    totalMessages: 230
  },
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane@example.com',
    avatar: '',
    role: 'user',
    status: 'active',
    createdAt: new Date('2024-02-10'),
    lastActive: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    totalChats: 23,
    totalMessages: 156
  },
  {
    id: '3',
    name: 'Admin User',
    email: 'admin@example.com',
    avatar: '',
    role: 'admin',
    status: 'active',
    createdAt: new Date('2024-01-01'),
    lastActive: new Date(),
    totalChats: 12,
    totalMessages: 89
  },
  {
    id: '4',
    name: 'Bob Wilson',
    email: 'bob@example.com',
    avatar: '',
    role: 'user',
    status: 'inactive',
    createdAt: new Date('2024-03-05'),
    lastActive: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7), // 7 days ago
    totalChats: 8,
    totalMessages: 34
  },
  {
    id: '5',
    name: 'Alice Brown',
    email: 'alice@example.com',
    avatar: '',
    role: 'user',
    status: 'banned',
    createdAt: new Date('2024-02-20'),
    lastActive: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
    totalChats: 67,
    totalMessages: 445
  }
];

const mockStatistics: ChatStatistics = {
  totalUsers: 125,
  totalChats: 456,
  totalMessages: 2340,
  activeUsers: 89,
  averageSessionLength: 12.5,
  popularPrompts: [
    'What can you help me with?',
    'Explain quantum computing',
    'Write a Python function',
    'Help me with SQL queries',
    'Analyze this data'
  ],
  messagesByDay: [
    { date: '2024-08-09', count: 45 },
    { date: '2024-08-10', count: 67 },
    { date: '2024-08-11', count: 89 },
    { date: '2024-08-12', count: 56 },
    { date: '2024-08-13', count: 78 },
    { date: '2024-08-14', count: 92 },
    { date: '2024-08-15', count: 134 }
  ],
  userGrowth: [
    { date: '2024-01', count: 12 },
    { date: '2024-02', count: 23 },
    { date: '2024-03', count: 34 },
    { date: '2024-04', count: 45 },
    { date: '2024-05', count: 67 },
    { date: '2024-06', count: 89 },
    { date: '2024-07', count: 112 },
    { date: '2024-08', count: 125 }
  ]
};

const mockSettings: SystemSettings = {
  maxFileSize: 10485760, // 10MB
  allowedFileTypes: ['image/*', '.pdf', '.doc', '.docx', '.txt', '.csv', '.json', '.xml'],
  maxChatHistory: 100,
  enableFileUpload: true,
  enablePromptTemplates: true,
  maintenanceMode: false,
  rateLimitPerMinute: 60
};

export const adminAPI = {
  // Get all admin dashboard data
  getDashboardData: async (): Promise<AdminDashboardData> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      users: mockUsers,
      statistics: mockStatistics,
      settings: mockSettings
    };
  },

  // Get users with pagination
  getUsers: async (page: number = 1, limit: number = 10): Promise<{ users: User[]; total: number }> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const start = (page - 1) * limit;
    const end = start + limit;
    const paginatedUsers = mockUsers.slice(start, end);
    
    return {
      users: paginatedUsers,
      total: mockUsers.length
    };
  },

  // Update user status
  updateUserStatus: async (userId: string, status: User['status']): Promise<User> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const userIndex = mockUsers.findIndex(u => u.id === userId);
    if (userIndex !== -1) {
      mockUsers[userIndex].status = status;
      return mockUsers[userIndex];
    }
    throw new Error('User not found');
  },

  // Delete user
  deleteUser: async (userId: string): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const userIndex = mockUsers.findIndex(u => u.id === userId);
    if (userIndex !== -1) {
      mockUsers.splice(userIndex, 1);
    } else {
      throw new Error('User not found');
    }
  },

  // Update system settings
  updateSettings: async (settings: Partial<SystemSettings>): Promise<SystemSettings> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    Object.assign(mockSettings, settings);
    return mockSettings;
  },

  // Get chat statistics
  getStatistics: async (): Promise<ChatStatistics> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockStatistics;
  }
};
