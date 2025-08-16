import React, { useState, useEffect } from 'react';
import { DatabaseConnection, DatabaseConnectionState } from '@/types/features/database';
import { DatabaseConnectionCard } from './DatabaseConnectionCard';
import { DatabaseConnectionForm } from './DatabaseConnectionForm';
import { Text2SQLInterface } from './Text2SQLInterface';
import { Button } from '@/components/shared/ui/Button';
import { Input } from '@/components/shared/ui/Input';
import { Select } from '@/components/shared/ui/Select';
import { 
  Plus, 
  Database, 
  Filter,
  Activity,
  BarChart3,
  Zap,
  Server
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface DatabaseManagerProps {
  onSelectConnection?: (connection: DatabaseConnection) => void;
  compact?: boolean;
}

export const DatabaseManager: React.FC<DatabaseManagerProps> = ({
  onSelectConnection,
  compact = false
}) => {
  const [state, setState] = useState<DatabaseConnectionState>({
    connections: [],
    activeConnectionId: null,
    isLoading: false,
    error: null,
    queryHistory: []
  });
  
  const [showForm, setShowForm] = useState(false);
  const [editingConnection, setEditingConnection] = useState<DatabaseConnection | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<'connections' | 'query'>('connections');

  // Mock data for demo
  const generateMockConnections = (): DatabaseConnection[] => [
    {
      id: '1',
      name: 'Production Database',
      type: 'postgresql',
      host: 'prod-db.company.com',
      port: 5432,
      database: 'ecommerce',
      username: 'app_user',
      schema: 'public',
      isActive: true,
      isConnected: true,
      lastConnected: new Date(),
      createdAt: new Date('2024-01-15'),
      updatedAt: new Date('2024-01-20'),
      metadata: {
        version: 'PostgreSQL 15.3',
        tables: [
          { name: 'users', schema: 'public', columns: [] },
          { name: 'orders', schema: 'public', columns: [] },
          { name: 'products', schema: 'public', columns: [] },
        ],
        schemas: ['public', 'analytics'],
        totalSize: '2.3 GB'
      }
    },
    {
      id: '2',
      name: 'Analytics Warehouse',
      type: 'mysql',
      host: 'analytics.company.com',
      port: 3306,
      database: 'data_warehouse',
      username: 'analyst',
      isActive: true,
      isConnected: false,
      createdAt: new Date('2024-01-10'),
      updatedAt: new Date('2024-01-18'),
      metadata: {
        version: 'MySQL 8.0.35',
        tables: [
          { name: 'sales_data', schema: 'analytics', columns: [] },
          { name: 'customer_metrics', schema: 'analytics', columns: [] },
        ],
        schemas: ['analytics'],
        totalSize: '15.7 GB'
      }
    },
    {
      id: '3',
      name: 'Development DB',
      type: 'sqlite',
      host: 'localhost',
      port: 0,
      database: '/tmp/dev.db',
      username: 'dev',
      isActive: true,
      isConnected: true,
      lastConnected: new Date(),
      createdAt: new Date('2024-01-05'),
      updatedAt: new Date('2024-01-22'),
      metadata: {
        version: 'SQLite 3.42.0',
        tables: [
          { name: 'test_users', schema: 'main', columns: [] },
          { name: 'test_data', schema: 'main', columns: [] },
        ],
        schemas: ['main'],
        totalSize: '45 MB'
      }
    }
  ];

  useEffect(() => {
    setState(prev => ({
      ...prev,
      connections: generateMockConnections()
    }));
  }, []);

  const filteredConnections = state.connections.filter(conn => {
    const matchesSearch = conn.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         conn.database.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         conn.host.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = filterType === 'all' || conn.type === filterType;
    
    return matchesSearch && matchesType;
  });

  const handleSaveConnection = async (connectionData: Omit<DatabaseConnection, 'id' | 'createdAt' | 'updatedAt' | 'isConnected' | 'lastConnected'>) => {
    try {
      if (editingConnection) {
        // Update existing
        const updated: DatabaseConnection = {
          ...editingConnection,
          ...connectionData,
          updatedAt: new Date(),
        };
        setState(prev => ({
          ...prev,
          connections: prev.connections.map(c => c.id === editingConnection.id ? updated : c)
        }));
      } else {
        // Create new
        const newConnection: DatabaseConnection = {
          ...connectionData,
          id: Math.random().toString(36).substr(2, 9),
          isConnected: false,
          createdAt: new Date(),
          updatedAt: new Date(),
        };
        setState(prev => ({
          ...prev,
          connections: [newConnection, ...prev.connections]
        }));
      }
      
      setShowForm(false);
      setEditingConnection(null);
    } catch (error) {
      setState(prev => ({ ...prev, error: 'Failed to save connection' }));
    }
  };

  const handleDeleteConnection = async (id: string) => {
    if (confirm('Are you sure you want to delete this connection?')) {
      setState(prev => ({
        ...prev,
        connections: prev.connections.filter(c => c.id !== id),
        activeConnectionId: prev.activeConnectionId === id ? null : prev.activeConnectionId
      }));
    }
  };

  const handleTestConnection = async (id: string) => {
    const connection = state.connections.find(c => c.id === id);
    if (!connection) return;

    // Simulate connection test
    const isSuccessful = Math.random() > 0.3; // 70% success rate for demo
    
    setState(prev => ({
      ...prev,
      connections: prev.connections.map(c => 
        c.id === id 
          ? { 
              ...c, 
              isConnected: isSuccessful,
              lastConnected: isSuccessful ? new Date() : c.lastConnected
            }
          : c
      )
    }));
  };

  const handleSelectConnection = (connection: DatabaseConnection) => {
    setState(prev => ({ ...prev, activeConnectionId: connection.id }));
    if (onSelectConnection) {
      onSelectConnection(connection);
    }
  };

  const handleEditConnection = (connection: DatabaseConnection) => {
    setEditingConnection(connection);
    setShowForm(true);
  };

  const connectedConnections = state.connections.filter(c => c.isConnected);

  if (compact) {
    return (
      <div className="space-y-4 h-full overflow-hidden">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
          <Input
            placeholder="Search connections..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 min-w-0"
          />
          <Button onClick={() => setShowForm(true)} size="sm" className="w-full sm:w-auto">
            <Plus className="h-4 w-4 sm:mr-2" />
            <span className="sm:inline">Add</span>
          </Button>
        </div>

        {showForm && (
          <div className="border rounded-lg p-4 bg-muted/30">
            <DatabaseConnectionForm
              connection={editingConnection || undefined}
              onSave={handleSaveConnection}
              onCancel={() => {
                setShowForm(false);
                setEditingConnection(null);
              }}
            />
          </div>
        )}

        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="grid gap-4 p-4">
            {filteredConnections.slice(0, 3).map((connection) => (
              <DatabaseConnectionCard
                key={connection.id}
                connection={connection}
                onEdit={handleEditConnection}
                onDelete={handleDeleteConnection}
                onTest={handleTestConnection}
                onSelect={handleSelectConnection}
                isSelected={connection.id === state.activeConnectionId}
              />
            ))}
          </div>
          
          {filteredConnections.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <Database className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No connections found</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="border-b p-4 lg:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div className="min-w-0 flex-1">
            <h1 className="text-xl lg:text-2xl font-bold flex items-center gap-2">
              <Database className="h-5 w-5 lg:h-6 lg:w-6" />
              Database Manager
            </h1>
            <p className="text-muted-foreground text-sm lg:text-base mt-1">
              Manage database connections and execute Text-to-SQL queries
            </p>
          </div>
          
          <Button onClick={() => setShowForm(true)} className="w-full sm:w-auto">
            <Plus className="h-4 w-4 mr-2" />
            <span className="sm:inline">New Connection</span>
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex rounded-lg bg-muted p-1 w-full sm:w-fit overflow-x-auto">
          <button
            onClick={() => setActiveTab('connections')}
            className={cn(
              'flex items-center gap-2 px-3 sm:px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap flex-1 sm:flex-initial justify-center sm:justify-start',
              activeTab === 'connections'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <Server className="h-4 w-4" />
            <span className="hidden xs:inline">Connections</span>
          </button>
          <button
            onClick={() => setActiveTab('query')}
            className={cn(
              'flex items-center gap-2 px-3 sm:px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap flex-1 sm:flex-initial justify-center sm:justify-start',
              activeTab === 'query'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <Zap className="h-4 w-4" />
            <span className="hidden xs:inline">Text-to-SQL</span>
          </button>
        </div>

        {/* Stats */}
        {activeTab === 'connections' && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4 mt-4">
            <div className="bg-muted/50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Database className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs sm:text-sm text-muted-foreground">Total</span>
              </div>
              <p className="text-xl lg:text-2xl font-bold">{state.connections.length}</p>
            </div>
            
            <div className="bg-muted/50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs sm:text-sm text-muted-foreground">Connected</span>
              </div>
              <p className="text-xl lg:text-2xl font-bold">{connectedConnections.length}</p>
            </div>
            
            <div className="bg-muted/50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs sm:text-sm text-muted-foreground">Active</span>
              </div>
              <p className="text-xl lg:text-2xl font-bold">{state.connections.filter(c => c.isActive).length}</p>
            </div>
            
            <div className="bg-muted/50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs sm:text-sm text-muted-foreground">Types</span>
              </div>
              <p className="text-xl lg:text-2xl font-bold">{new Set(state.connections.map(c => c.type)).size}</p>
            </div>
          </div>
        )}

        {/* Filters - Only for connections tab */}
        {activeTab === 'connections' && (
          <div className="flex flex-col sm:flex-row gap-3 mt-4">
            <div className="flex-1 min-w-0">
              <Input
                placeholder="Search connections..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            
            <div className="w-full sm:w-auto sm:min-w-[160px]">
              <Select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="w-full"
              >
                <option value="all">All Types</option>
                <option value="postgresql">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="sqlite">SQLite</option>
                <option value="mssql">SQL Server</option>
                <option value="oracle">Oracle</option>
                <option value="mongodb">MongoDB</option>
                <option value="redis">Redis</option>
              </Select>
            </div>
          </div>
        )}
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <DatabaseConnectionForm
              connection={editingConnection || undefined}
              onSave={handleSaveConnection}
              onCancel={() => {
                setShowForm(false);
                setEditingConnection(null);
              }}
              onTest={async (_data) => {
                // Mock test function
                const success = Math.random() > 0.3;
                return {
                  success,
                  message: success ? 'Connection successful!' : 'Connection failed. Please check your credentials.'
                };
              }}
            />
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'connections' ? (
          <div className="p-4 lg:p-6 h-full overflow-y-auto">
            {filteredConnections.length === 0 ? (
              <div className="flex items-center justify-center h-32 text-center">
                <div>
                  <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No connections found</h3>
                  <p className="text-muted-foreground mb-4 text-sm lg:text-base">
                    {searchTerm ? 'Try adjusting your search' : 'Create your first database connection'}
                  </p>
                  {!searchTerm && (
                    <Button onClick={() => setShowForm(true)} className="w-full sm:w-auto">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Connection
                    </Button>
                  )}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4 p-4">
                {filteredConnections.map((connection) => (
                  <DatabaseConnectionCard
                    key={connection.id}
                    connection={connection}
                    onEdit={handleEditConnection}
                    onDelete={handleDeleteConnection}
                    onTest={handleTestConnection}
                    onSelect={handleSelectConnection}
                    isSelected={connection.id === state.activeConnectionId}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          <Text2SQLInterface
            connections={connectedConnections.map(c => ({
              id: c.id,
              name: c.name,
              isConnected: c.isConnected
            }))}
            activeConnectionId={state.activeConnectionId}
            onConnectionChange={(id: string) => setState(prev => ({ ...prev, activeConnectionId: id }))}
            onGenerateSQL={async (_request: string) => {
              // Mock Text-to-SQL generation
              const mockResponses = [
                {
                  sql: `SELECT u.name, u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
GROUP BY u.id, u.name, u.email
ORDER BY order_count DESC;`,
                  explanation: "This query finds all users who signed up in the last month and shows how many orders each has placed, sorted by order count."
                },
                {
                  sql: `SELECT p.name, p.price, SUM(oi.quantity) as total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
GROUP BY p.id, p.name, p.price
ORDER BY total_sold DESC
LIMIT 10;`,
                  explanation: "This query returns the top 10 best-selling products in the last 3 months based on total quantity sold."
                }
              ];
              
              return mockResponses[Math.floor(Math.random() * mockResponses.length)];
            }}
            onExecuteSQL={async (_sql: string) => {
              // Mock SQL execution
              return {
                results: {
                  columns: ['id', 'name', 'email', 'created_at'],
                  rows: [
                    { id: 1, name: 'John Doe', email: 'john@example.com', created_at: '2024-01-15' },
                    { id: 2, name: 'Jane Smith', email: 'jane@example.com', created_at: '2024-01-16' },
                  ],
                  rowCount: 2
                },
                executionTime: 45
              };
            }}
            queryHistory={state.queryHistory.filter(q => q.executedAt).map(q => ({
              naturalLanguage: q.naturalLanguage,
              generatedSQL: q.generatedSQL,
              executedAt: q.executedAt!
            }))}
          />
        )}
      </div>
    </div>
  );
};
