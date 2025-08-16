import React, { useState, useEffect } from 'react';
import {
  Connection,
  ConnectionState,
  ConnectionTemplate,
  ConnectionDashboardStats
} from '@/types/features/connections';
import { ConnectionForm } from './ConnectionForm';
import { ConnectionTemplateGrid } from './ConnectionTemplateGrid';
import { ConnectionStatsGrid } from './ConnectionStatsGrid';
import '@/styles/components/julius-ai-styles.css';
import {
  Plus,
  Search,
  RefreshCw,
  Grid,
  Settings,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  Globe,
  Database,
  Webhook,
  Key,
  Folder,
  MessageSquare,
  BarChart,
  CreditCard,
  Mail,
  Smartphone,
  Share2,
  Users,
  Building,
  Plug
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { connectionAPI } from '@/lib/connectionAPI';

interface ConnectionDashboardProps {
  onSelectConnection?: (connection: Connection) => void;
  compact?: boolean;
}

export const ConnectionDashboard: React.FC<ConnectionDashboardProps> = ({
  onSelectConnection,
  compact = false
}) => {
  const [state, setState] = useState<ConnectionState>({
    connections: [],
    templates: [],
    selectedConnection: null,
    isLoading: false,
    error: null,
    filters: {},
    pagination: {
      page: 1,
      limit: 20,
      total: 0
    }
  });

  const [stats, setStats] = useState<ConnectionDashboardStats | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingConnection, setEditingConnection] = useState<Connection | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<ConnectionTemplate | null>(null);
  const [activeTab, setActiveTab] = useState<'connections' | 'templates' | 'stats'>('connections');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadConnections();
    loadTemplates();
    loadStats();
  }, [state.pagination.page, state.pagination.limit, state.filters]);

  const loadConnections = async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const params = {
        page: state.pagination.page,
        limit: state.pagination.limit,
        ...(searchTerm && { search: searchTerm })
      };

      const response = await connectionAPI.getConnections(params);
      
      setState(prev => ({
        ...prev,
        connections: response.connections,
        pagination: {
          ...prev.pagination,
          total: response.total
        },
        isLoading: false
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to load connections',
        isLoading: false
      }));
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await connectionAPI.getConnectionTemplates();
      setState(prev => ({
        ...prev,
        templates: response.templates
      }));
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await connectionAPI.getConnectionStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleCreateConnection = async (connectionData: any) => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      await connectionAPI.createConnection(connectionData);
      setShowForm(false);
      setSelectedTemplate(null);
      setEditingConnection(null);
      await loadConnections();
      await loadStats();
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to create connection',
        isLoading: false
      }));
    }
  };

  const handleUpdateConnection = async (connectionData: any) => {
    if (!editingConnection) return;
    
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      await connectionAPI.updateConnection(editingConnection.id, connectionData);
      setShowForm(false);
      setEditingConnection(null);
      await loadConnections();
      await loadStats();
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to update connection',
        isLoading: false
      }));
    }
  };

  const handleDeleteConnection = async (connectionId: string) => {
    if (!confirm('Are you sure you want to delete this connection?')) return;
    
    try {
      await connectionAPI.deleteConnection(connectionId);
      await loadConnections();
      await loadStats();
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to delete connection'
      }));
    }
  };

  const handleTestConnection = async (connectionId: string) => {
    try {
      await connectionAPI.testExistingConnection(connectionId);
      await loadConnections(); // Refresh to get updated status
    } catch (error) {
      console.error('Connection test failed:', error);
    }
  };

  const handleEditConnection = (connection: Connection) => {
    setEditingConnection(connection);
    setShowForm(true);
    setSelectedTemplate(null);
  };

  const handleSelectTemplate = (template: ConnectionTemplate) => {
    setSelectedTemplate(template);
    setShowForm(true);
    setEditingConnection(null);
  };

  const handleRefresh = () => {
    loadConnections();
    loadStats();
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setState(prev => ({
      ...prev,
      pagination: { ...prev.pagination, page: 1 }
    }));
  };

  const getTypeIcon = (type: string) => {
    const iconClass = "h-4 w-4 text-blue-600";
    switch (type) {
      case 'api':
        return <Globe className={iconClass} />;
      case 'database':
        return <Database className={iconClass} />;
      case 'webhook':
        return <Webhook className={iconClass} />;
      case 'oauth':
        return <Key className={iconClass} />;
      case 'file_storage':
        return <Folder className={iconClass} />;
      case 'messaging':
        return <MessageSquare className={iconClass} />;
      case 'analytics':
        return <BarChart className={iconClass} />;
      case 'payment':
        return <CreditCard className={iconClass} />;
      case 'email':
        return <Mail className={iconClass} />;
      case 'sms':
        return <Smartphone className={iconClass} />;
      case 'social_media':
        return <Share2 className={iconClass} />;
      case 'crm':
        return <Users className={iconClass} />;
      case 'erp':
        return <Building className={iconClass} />;
      case 'custom':
        return <Settings className={iconClass} />;
      default:
        return <Plug className={iconClass} />;
    }
  };



  if (showForm) {
    return (
      <ConnectionForm
        connection={editingConnection || undefined}
        template={selectedTemplate || undefined}
        onSave={editingConnection ? handleUpdateConnection : handleCreateConnection}
        onCancel={() => {
          setShowForm(false);
          setEditingConnection(null);
          setSelectedTemplate(null);
        }}
        onTest={async (connectionData) => {
          return await connectionAPI.testConnection({
            connectionData,
            testEndpoint: undefined,
            testMethod: 'GET'
          });
        }}
        isLoading={state.isLoading}
      />
    );
  }

  return (
    <div className="h-full flex julius-main-content">
      {/* Sidebar - Julius AI Style */}
      <div className="julius-sidebar">
        {/* Sidebar Header */}
        <div className="julius-sidebar-header">
          <div className="flex items-center space-x-3">
            <div className="julius-logo">
              <Settings className="h-4 w-4" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 text-sm">Data Connectors & MCPs</h2>
            </div>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            You can connect Julius to your data stores and business tools here.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex-1 p-4">
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab('connections')}
              className={cn(
                "julius-nav-item",
                activeTab === 'connections' && "active"
              )}
            >
              <Settings className="h-4 w-4" />
              My Connections
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={cn(
                "julius-nav-item",
                activeTab === 'templates' && "active"
              )}
            >
              <Grid className="h-4 w-4" />
              Add connectors
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={cn(
                "julius-nav-item",
                activeTab === 'stats' && "active"
              )}
            >
              <Activity className="h-4 w-4" />
              Statistics
            </button>
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-2">
            <div className="font-medium">Resources</div>
            <div className="space-y-1">
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">📚 Documentation</a>
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">💬 Community Slack</a>
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">🧪 Models Lab</a>
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">⬆️ Upgrade Subscription</a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <div className="julius-header">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {activeTab === 'connections' && 'My Connections'}
                {activeTab === 'templates' && 'Add connectors'}
                {activeTab === 'stats' && 'Statistics'}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {activeTab === 'connections' && 'Manage your active connections'}
                {activeTab === 'templates' && 'Choose from available connectors'}
                {activeTab === 'stats' && 'View connection analytics and performance'}
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleRefresh}
                className="julius-btn julius-btn-secondary"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
              {activeTab === 'connections' && (
                <button
                  onClick={() => setShowForm(true)}
                  className="julius-btn julius-btn-primary"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden julius-content">
          {activeTab === 'connections' && (
            <div className="p-6">
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">My Connections</h2>

                {/* Connections Table - Julius AI Style */}
                {state.connections.length > 0 ? (
                  <div className="julius-connections-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Connector</th>
                          <th>Type</th>
                          <th>Created</th>
                          <th>Status</th>
                          <th></th>
                        </tr>
                      </thead>
                      <tbody>
                        {state.connections.map((connection) => (
                          <tr key={connection.id}>
                            <td>
                              <div className="flex items-center">
                                <div className="julius-connection-icon mr-3">
                                  {getTypeIcon(connection.type)}
                                </div>
                                <div>
                                  <div className="text-sm font-medium text-gray-900">
                                    {connection.name}
                                  </div>
                                  <div className="text-sm text-gray-500">
                                    {connection.provider}
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td>
                              <span className="julius-badge julius-badge-gray">
                                {connection.type === 'api' ? 'MCP' : connection.type.toUpperCase()}
                              </span>
                            </td>
                            <td className="text-sm text-gray-500">
                              {connection.createdAt ? new Date(connection.createdAt).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric'
                              }) : 'N/A'}
                            </td>
                            <td>
                              <span className={cn(
                                "julius-badge",
                                connection.status === 'active' ? "julius-badge-green" :
                                connection.status === 'error' ? "julius-badge-red" :
                                "julius-badge-yellow"
                              )}>
                                {connection.status}
                              </span>
                            </td>
                            <td className="text-right">
                              <button className="text-gray-400 hover:text-gray-600 p-1">
                                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                                </svg>
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="julius-empty-state">
                    <Settings className="julius-empty-icon" />
                    <h3 className="julius-empty-title">No connections yet</h3>
                    <p className="julius-empty-description">
                      Get started by adding your first connection
                    </p>
                    <button
                      onClick={() => setShowForm(true)}
                      className="julius-btn julius-btn-primary"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Connection
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <ConnectionTemplateGrid
              templates={state.templates}
              onSelectTemplate={handleSelectTemplate}
            />
          )}

          {activeTab === 'stats' && (
            <ConnectionStatsGrid stats={stats} />
          )}
        </div>
      </div>
    </div>
  );
};
