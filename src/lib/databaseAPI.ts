import { DatabaseConnection, SQLQuery, Text2SQLRequest, DatabaseMetadata } from '@/types/database';

const API_BASE_URL = '/api';

export const databaseAPI = {
  // Database Connections
  async getConnections(): Promise<DatabaseConnection[]> {
    const response = await fetch(`${API_BASE_URL}/database/connections`);
    if (!response.ok) {
      throw new Error('Failed to fetch database connections');
    }
    return response.json();
  },

  async createConnection(connection: Omit<DatabaseConnection, 'id' | 'createdAt' | 'updatedAt' | 'isConnected' | 'lastConnected'>): Promise<DatabaseConnection> {
    const response = await fetch(`${API_BASE_URL}/database/connections`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(connection),
    });

    if (!response.ok) {
      throw new Error('Failed to create database connection');
    }

    return response.json();
  },

  async updateConnection(id: string, connection: Partial<DatabaseConnection>): Promise<DatabaseConnection> {
    const response = await fetch(`${API_BASE_URL}/database/connections/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(connection),
    });

    if (!response.ok) {
      throw new Error('Failed to update database connection');
    }

    return response.json();
  },

  async deleteConnection(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/database/connections/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete database connection');
    }
  },

  async testConnection(id: string): Promise<{ success: boolean; message: string; metadata?: DatabaseMetadata }> {
    const response = await fetch(`${API_BASE_URL}/database/connections/${id}/test`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to test database connection');
    }

    return response.json();
  },

  async getConnectionMetadata(id: string): Promise<DatabaseMetadata> {
    const response = await fetch(`${API_BASE_URL}/database/connections/${id}/metadata`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch database metadata');
    }

    return response.json();
  },

  // Text-to-SQL functionality
  async generateSQL(request: Text2SQLRequest): Promise<{ sql: string; explanation: string }> {
    const response = await fetch(`${API_BASE_URL}/database/text2sql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('Failed to generate SQL from text');
    }

    return response.json();
  },

  async executeSQL(connectionId: string, sql: string): Promise<SQLQuery> {
    const response = await fetch(`${API_BASE_URL}/database/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ connectionId, sql }),
    });

    if (!response.ok) {
      throw new Error('Failed to execute SQL query');
    }

    return response.json();
  },

  async getQueryHistory(connectionId?: string): Promise<SQLQuery[]> {
    const url = connectionId 
      ? `${API_BASE_URL}/database/queries?connectionId=${connectionId}`
      : `${API_BASE_URL}/database/queries`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch query history');
    }

    return response.json();
  },

  // Schema exploration
  async getTables(connectionId: string, schema?: string): Promise<string[]> {
    const url = schema 
      ? `${API_BASE_URL}/database/connections/${connectionId}/tables?schema=${schema}`
      : `${API_BASE_URL}/database/connections/${connectionId}/tables`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch tables');
    }

    return response.json();
  },

  async getTableSchema(connectionId: string, tableName: string, schema?: string): Promise<any> {
    const params = new URLSearchParams({ table: tableName });
    if (schema) params.append('schema', schema);
    
    const response = await fetch(`${API_BASE_URL}/database/connections/${connectionId}/schema?${params}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch table schema');
    }

    return response.json();
  },
};
