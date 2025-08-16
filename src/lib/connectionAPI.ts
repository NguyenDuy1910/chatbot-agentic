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

const API_BASE_URL = '/api';

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
    
    const url = `${API_BASE_URL}/connections${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch connections');
    }

    return response.json();
  },

  async getConnection(id: string): Promise<{ connection: Connection }> {
    const response = await fetch(`${API_BASE_URL}/connections/${id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch connection');
    }

    return response.json();
  },

  async createConnection(connectionData: ConnectionFormData): Promise<{ connection: Connection }> {
    const response = await fetch(`${API_BASE_URL}/connections`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(connectionData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create connection');
    }

    return response.json();
  },

  async updateConnection(id: string, connectionData: Partial<ConnectionFormData>): Promise<{ connection: Connection }> {
    const response = await fetch(`${API_BASE_URL}/connections/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(connectionData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update connection');
    }

    return response.json();
  },

  async deleteConnection(id: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/connections/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete connection');
    }

    return response.json();
  },

  // Connection testing
  async testConnection(testData: ConnectionTestRequest): Promise<ConnectionTestResult> {
    const response = await fetch(`${API_BASE_URL}/connections/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(testData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to test connection');
    }

    return response.json();
  },

  async testExistingConnection(
    id: string, 
    testEndpoint?: string, 
    testMethod?: string
  ): Promise<ConnectionTestResult> {
    const params = new URLSearchParams();
    if (testEndpoint) params.append('test_endpoint', testEndpoint);
    if (testMethod) params.append('test_method', testMethod);
    
    const url = `${API_BASE_URL}/connections/${id}/test${params.toString() ? `?${params.toString()}` : ''}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to test connection');
    }

    return response.json();
  },

  // Templates and metadata
  async getConnectionTemplates(): Promise<ConnectionTemplateResponse> {
    const response = await fetch(`${API_BASE_URL}/connections/templates`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch connection templates');
    }

    return response.json();
  },

  // Statistics and monitoring
  async getConnectionStats(): Promise<ConnectionDashboardStats> {
    const response = await fetch(`${API_BASE_URL}/connections/stats`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch connection statistics');
    }

    return response.json();
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
    
    const url = `${API_BASE_URL}/connections/${connectionId}/logs${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch connection logs');
    }

    return response.json();
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
