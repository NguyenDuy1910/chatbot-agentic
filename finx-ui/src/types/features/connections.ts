// Connection Management Types
// Comprehensive types for external service connections similar to Julius AI

export type ConnectionType = 
  | 'api'
  | 'database'
  | 'webhook'
  | 'oauth'
  | 'file_storage'
  | 'messaging'
  | 'analytics'
  | 'payment'
  | 'email'
  | 'sms'
  | 'social_media'
  | 'crm'
  | 'erp'
  | 'custom';

export type ConnectionStatus = 'active' | 'inactive' | 'error' | 'testing' | 'pending';

export type AuthenticationType = 
  | 'none'
  | 'api_key'
  | 'bearer_token'
  | 'basic_auth'
  | 'oauth2'
  | 'oauth1'
  | 'custom_header'
  | 'certificate'
  | 'jwt';

export interface ConnectionCredentials {
  type: AuthenticationType;
  apiKey?: string;
  bearerToken?: string;
  username?: string;
  password?: string;
  clientId?: string;
  clientSecret?: string;
  accessToken?: string;
  refreshToken?: string;
  customHeaders?: Record<string, string>;
  certificate?: string;
  privateKey?: string;
  additionalFields?: Record<string, any>;
}

export interface ConnectionConfig {
  baseUrl?: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  rateLimit?: {
    requests: number;
    period: number; // in seconds
  };
  customSettings?: Record<string, any>;
}

export interface ConnectionHealthCheck {
  enabled: boolean;
  interval: number; // in minutes
  endpoint?: string;
  method?: 'GET' | 'POST' | 'HEAD';
  expectedStatus?: number;
  timeout?: number;
}

export interface Connection {
  id: string;
  name: string;
  description?: string;
  type: ConnectionType;
  provider: string; // e.g., 'stripe', 'slack', 'google', 'custom'
  status: ConnectionStatus;
  isActive: boolean;
  
  // Configuration
  config: ConnectionConfig;
  credentials: ConnectionCredentials;
  healthCheck: ConnectionHealthCheck;
  
  // Metadata
  tags?: string[];
  category?: string;
  version?: string;
  
  // Status tracking
  lastConnected?: Date;
  lastHealthCheck?: Date;
  lastError?: string;
  errorCount: number;
  successCount: number;
  
  // Audit fields
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}

export interface ConnectionTemplate {
  id: string;
  name: string;
  description: string;
  type: ConnectionType;
  provider: string;
  icon?: string;
  category: string;
  
  // Template configuration
  configSchema: Record<string, any>; // JSON schema for config validation
  credentialsSchema: Record<string, any>; // JSON schema for credentials
  defaultConfig: Partial<ConnectionConfig>;
  defaultHealthCheck: Partial<ConnectionHealthCheck>;
  
  // Documentation
  documentation?: string;
  setupInstructions?: string;
  exampleUsage?: string;
  
  // Metadata
  isPopular?: boolean;
  isOfficial?: boolean;
  tags?: string[];
}

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  responseTime?: number;
  statusCode?: number;
  error?: string;
  details?: Record<string, any>;
  timestamp: Date;
}

export interface ConnectionUsageStats {
  connectionId: string;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  lastUsed?: Date;
  usageByDay: Array<{
    date: string;
    requests: number;
    errors: number;
  }>;
}

export interface ConnectionLog {
  id: string;
  connectionId: string;
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  details?: Record<string, any>;
  timestamp: Date;
  userId?: string;
}

// State management interfaces
export interface ConnectionState {
  connections: Connection[];
  templates: ConnectionTemplate[];
  selectedConnection: Connection | null;
  isLoading: boolean;
  error: string | null;
  filters: {
    type?: ConnectionType;
    status?: ConnectionStatus;
    provider?: string;
    search?: string;
  };
  pagination: {
    page: number;
    limit: number;
    total: number;
  };
}

// Form interfaces
export interface ConnectionFormData {
  name: string;
  description?: string;
  type: ConnectionType;
  provider: string;
  config: ConnectionConfig;
  credentials: ConnectionCredentials;
  healthCheck: ConnectionHealthCheck;
  tags?: string[];
  category?: string;
  isActive: boolean;
}

export interface ConnectionTestRequest {
  connectionData: ConnectionFormData;
  testEndpoint?: string;
  testMethod?: 'GET' | 'POST' | 'HEAD';
}

// API response interfaces
export interface ConnectionResponse {
  connection: Connection;
  testResult?: ConnectionTestResult;
}

export interface ConnectionListResponse {
  connections: Connection[];
  total: number;
  page: number;
  limit: number;
}

export interface ConnectionTemplateResponse {
  templates: ConnectionTemplate[];
  categories: string[];
  providers: string[];
}

// Dashboard interfaces
export interface ConnectionDashboardStats {
  totalConnections: number;
  activeConnections: number;
  errorConnections: number;
  recentlyUsed: number;
  averageResponseTime: number;
  uptime: number;
  connectionsByType: Record<ConnectionType, number>;
  connectionsByStatus: Record<ConnectionStatus, number>;
}

export interface ConnectionAlert {
  id: string;
  connectionId: string;
  connectionName: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  timestamp: Date;
  acknowledged: boolean;
}
