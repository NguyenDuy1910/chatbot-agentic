import { DatabaseConnection, SQLQuery, Text2SQLRequest, DatabaseMetadata } from '@/types/features/database';
import { api } from './api';
import { apiConfig } from '@/config/api';

export const databaseAPI = {
  // Database Connections - Note: These might need to be mapped to connection endpoints
  async getConnections(): Promise<DatabaseConnection[]> {
    // Database connections might be handled through the connections API
    return api.get<DatabaseConnection[]>(apiConfig.endpoints.connections.base);
  },

  async createConnection(connection: Omit<DatabaseConnection, 'id' | 'createdAt' | 'updatedAt' | 'isConnected' | 'lastConnected'>): Promise<DatabaseConnection> {
    return api.post<DatabaseConnection>(apiConfig.endpoints.connections.base, connection);
  },

  async updateConnection(id: string, connection: Partial<DatabaseConnection>): Promise<DatabaseConnection> {
    return api.put<DatabaseConnection>(apiConfig.endpoints.connections.byId(id), connection);
  },

  async deleteConnection(id: string): Promise<void> {
    await api.delete(apiConfig.endpoints.connections.byId(id));
  },

  async testConnection(id: string): Promise<{ success: boolean; message: string; metadata?: DatabaseMetadata }> {
    return api.post<{ success: boolean; message: string; metadata?: DatabaseMetadata }>(apiConfig.endpoints.connections.testById(id));
  },

  async getConnectionMetadata(id: string): Promise<DatabaseMetadata> {
    return api.get<DatabaseMetadata>(`${apiConfig.endpoints.connections.byId(id)}/metadata`);
  },

  // Text-to-SQL functionality - These endpoints might need to be created in backend
  async generateSQL(request: Text2SQLRequest): Promise<{ sql: string; explanation: string }> {
    // Note: This endpoint might need to be implemented in backend
    return api.post<{ sql: string; explanation: string }>('/api/v1/database/text2sql', request);
  },

  async executeSQL(connectionId: string, sql: string): Promise<SQLQuery> {
    // Note: This endpoint might need to be implemented in backend
    return api.post<SQLQuery>('/api/v1/database/execute', { connectionId, sql });
  },

  async getQueryHistory(connectionId?: string): Promise<SQLQuery[]> {
    const endpoint = connectionId
      ? `/api/v1/database/queries?connectionId=${connectionId}`
      : '/api/v1/database/queries';

    return api.get<SQLQuery[]>(endpoint);
  },

  // Schema exploration
  async getTables(connectionId: string, schema?: string): Promise<string[]> {
    const endpoint = schema
      ? `${apiConfig.endpoints.connections.byId(connectionId)}/tables?schema=${schema}`
      : `${apiConfig.endpoints.connections.byId(connectionId)}/tables`;

    return api.get<string[]>(endpoint);
  },

  async getTableSchema(connectionId: string, tableName: string, schema?: string): Promise<any> {
    const params = new URLSearchParams({ table: tableName });
    if (schema) params.append('schema', schema);

    const endpoint = `${apiConfig.endpoints.connections.byId(connectionId)}/schema?${params}`;

    return api.get<any>(endpoint);
  },
};
