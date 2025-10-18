export interface DatabaseConnection {
  id: string;
  name: string;
  type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  password?: string;
  schema?: string;
  connectionString?: string;
  isActive: boolean;
  isConnected: boolean;
  lastConnected?: Date;
  createdAt: Date;
  updatedAt: Date;
  metadata?: DatabaseMetadata;
}

export type DatabaseType = 
  | 'postgresql'
  | 'mysql'
  | 'sqlite'
  | 'mssql'
  | 'oracle'
  | 'mongodb'
  | 'redis';

export interface DatabaseMetadata {
  version?: string;
  tables: DatabaseTableInfo[];
  schemas: string[];
  totalSize?: string;
}

export interface DatabaseTableInfo {
  name: string;
  schema: string;
  columns: DatabaseColumnInfo[];
  rowCount?: number;
  description?: string;
}

export interface DatabaseColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  primaryKey: boolean;
  foreignKey?: DatabaseForeignKeyInfo;
  description?: string;
}

export interface DatabaseForeignKeyInfo {
  table: string;
  column: string;
  schema?: string;
}

// Aliases for backward compatibility
export type TableInfo = DatabaseTableInfo;
export type ColumnInfo = DatabaseColumnInfo;
export type ForeignKeyInfo = DatabaseForeignKeyInfo;

export interface SQLQuery {
  id: string;
  naturalLanguage: string;
  generatedSQL: string;
  connectionId: string;
  executedAt?: Date;
  results?: QueryResult;
  error?: string;
  executionTime?: number;
}

export interface QueryResult {
  columns: string[];
  rows: any[];
  rowCount: number;
  affectedRows?: number;
}

export interface Text2SQLRequest {
  query: string;
  connectionId: string;
  context?: string;
  includeSchema?: boolean;
}

export interface DatabaseConnectionState {
  connections: DatabaseConnection[];
  activeConnectionId: string | null;
  isLoading: boolean;
  error: string | null;
  queryHistory: SQLQuery[];
}
