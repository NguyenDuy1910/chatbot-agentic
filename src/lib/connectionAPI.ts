import {
  Connection,
  ConnectionFormData,
  ConnectionTestRequest,
  ConnectionTestResult,
  ConnectionTemplate,
  ConnectionListResponse,
  ConnectionTemplateResponse,
  ConnectionDashboardStats,
  ConnectionLog,
  ConnectionType,
  ConnectionStatus
} from '@/types/features/connections';
import { api } from './api';
import { apiConfig } from '@/config/api';

export const connectionAPI = {
  // Connection CRUD operations
  async getConnections(params?: {
    page?: number;
    limit?: number;
    type?: ConnectionType;
    status?: ConnectionStatus;
    provider?: string;
    search?: string;
  }): Promise<ConnectionListResponse> {
    const searchParams = new URLSearchParams();

    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.type) searchParams.append('type', params.type);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.provider) searchParams.append('provider', params.provider);
    if (params?.search) searchParams.append('search', params.search);

    const endpoint = `${apiConfig.endpoints.connections.base}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;

    return api.get<ConnectionListResponse>(endpoint);
  },

  async getConnection(id: string): Promise<{ connection: Connection }> {
    return api.get<{ connection: Connection }>(apiConfig.endpoints.connections.byId(id));
  },

  async createConnection(connectionData: ConnectionFormData): Promise<{ connection: Connection }> {
    return api.post<{ connection: Connection }>(apiConfig.endpoints.connections.base, connectionData);
  },

  async updateConnection(id: string, connectionData: Partial<ConnectionFormData>): Promise<{ connection: Connection }> {
    return api.put<{ connection: Connection }>(apiConfig.endpoints.connections.byId(id), connectionData);
  },

  async deleteConnection(id: string): Promise<{ message: string }> {
    return api.delete<{ message: string }>(apiConfig.endpoints.connections.byId(id));
  },

  // Connection testing
  async testConnection(testData: ConnectionTestRequest): Promise<ConnectionTestResult> {
    return api.post<ConnectionTestResult>(apiConfig.endpoints.connections.test, testData);
  },

  async testExistingConnection(
    id: string,
    testEndpoint?: string,
    testMethod?: string
  ): Promise<ConnectionTestResult> {
    const params = new URLSearchParams();
    if (testEndpoint) params.append('test_endpoint', testEndpoint);
    if (testMethod) params.append('test_method', testMethod);

    const endpoint = `${apiConfig.endpoints.connections.testById(id)}${params.toString() ? `?${params.toString()}` : ''}`;

    return api.post<ConnectionTestResult>(endpoint);
  },

  // Templates and metadata
  async getConnectionTemplates(): Promise<ConnectionTemplateResponse> {
    return api.get<ConnectionTemplateResponse>(apiConfig.endpoints.connections.templates);
  },

  // Statistics and monitoring
  async getConnectionStats(): Promise<ConnectionDashboardStats> {
    return api.get<ConnectionDashboardStats>(apiConfig.endpoints.connections.stats);
  },

  // Logs
  async getConnectionLogs(
    connectionId: string,
    params?: {
      page?: number;
      limit?: number;
      level?: string;
    }
  ): Promise<{
    logs: ConnectionLog[];
    total: number;
    page: number;
    limit: number;
  }> {
    const searchParams = new URLSearchParams();

    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.level) searchParams.append('level', params.level);

    const endpoint = `${apiConfig.endpoints.connections.logs(connectionId)}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;

    return api.get<{
      logs: ConnectionLog[];
      total: number;
      page: number;
      limit: number;
    }>(endpoint);
  },

  // Health check utilities
  async performHealthCheck(connectionId: string): Promise<ConnectionTestResult> {
    return this.testExistingConnection(connectionId);
  },

  async performBulkHealthCheck(connectionIds: string[]): Promise<Record<string, ConnectionTestResult>> {
    const results: Record<string, ConnectionTestResult> = {};
    
    // Perform health checks in parallel with some concurrency control
    const chunks = [];
    const chunkSize = 5; // Test 5 connections at a time
    
    for (let i = 0; i < connectionIds.length; i += chunkSize) {
      chunks.push(connectionIds.slice(i, i + chunkSize));
    }
    
    for (const chunk of chunks) {
      const promises = chunk.map(async (id) => {
        try {
          const result = await this.performHealthCheck(id);
          return { id, result };
        } catch (error) {
          return {
            id,
            result: {
              success: false,
              message: 'Health check failed',
              error: error instanceof Error ? error.message : 'Unknown error',
              timestamp: new Date()
            } as ConnectionTestResult
          };
        }
      });
      
      const chunkResults = await Promise.all(promises);
      chunkResults.forEach(({ id, result }) => {
        results[id] = result;
      });
    }
    
    return results;
  },

  // Utility methods
  getConnectionStatusColor(status: ConnectionStatus): string {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'inactive':
        return 'text-gray-600 bg-gray-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'testing':
        return 'text-blue-600 bg-blue-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  },

  getConnectionTypeIcon(type: ConnectionType): string {
    switch (type) {
      case 'api':
        return 'globe';
      case 'database':
        return 'database';
      case 'webhook':
        return 'webhook';
      case 'oauth':
        return 'key';
      case 'file_storage':
        return 'folder';
      case 'messaging':
        return 'message-square';
      case 'analytics':
        return 'bar-chart';
      case 'payment':
        return 'credit-card';
      case 'email':
        return 'mail';
      case 'sms':
        return 'smartphone';
      case 'social_media':
        return 'share-2';
      case 'crm':
        return 'users';
      case 'erp':
        return 'building';
      case 'custom':
        return 'settings';
      default:
        return 'plug';
    }
  }
};
