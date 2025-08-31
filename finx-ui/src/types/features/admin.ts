export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'user' | 'admin';
  status: 'active' | 'inactive' | 'banned';
  createdAt: Date;
  lastActive: Date;
  totalChats: number;
  totalMessages: number;
}

export interface ChatStatistics {
  totalUsers: number;
  totalChats: number;
  totalMessages: number;
  activeUsers: number;
  averageSessionLength: number;
  popularPrompts: string[];
  messagesByDay: { date: string; count: number }[];
  userGrowth: { date: string; count: number }[];
}

export interface SystemSettings {
  maxFileSize: number;
  allowedFileTypes: string[];
  maxChatHistory: number;
  enableFileUpload: boolean;
  enablePromptTemplates: boolean;
  maintenanceMode: boolean;
  rateLimitPerMinute: number;
}

export interface AdminDashboardData {
  users: User[];
  statistics: ChatStatistics;
  settings: SystemSettings;
}
