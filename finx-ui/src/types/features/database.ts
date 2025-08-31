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
  tables: TableInfo[];
  schemas: string[];
  totalSize?: string;
}

export interface TableInfo {
  name: string;
  schema: string;
  columns: ColumnInfo[];
  rowCount?: number;
  description?: string;
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  primaryKey: boolean;
  foreignKey?: ForeignKeyInfo;
  description?: string;
}

export interface ForeignKeyInfo {
  table: string;
  column: string;
  schema?: string;
}

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
