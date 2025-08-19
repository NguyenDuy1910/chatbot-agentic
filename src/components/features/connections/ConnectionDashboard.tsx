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
import {
  Button,
  Input,
  Card,
  CardBody,
  Chip,
  Tabs,
  Tab,
  useDisclosure,
  Spinner,
} from '@heroui/react';
import {
  Plus,
  Search,
  RefreshCw,
  Grid3X3,
  List,
  Settings,
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
  Plug,
  TrendingUp,
} from 'lucide-react';
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
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedType, setSelectedType] = useState<string>('all');
  const { isOpen: isFormOpen, onOpen: onFormOpen, onClose: onFormClose } = useDisclosure();

  useEffect(() => {
    loadConnections();
    loadTemplates();
    loadStats();
  }, []);

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
      await loadConnections();
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

  const getTypeIcon = (type: string) => {
    const iconClass = "h-5 w-5";
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'error':
        return 'danger';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const connectionTypes = ['all', 'api', 'database', 'webhook', 'oauth', 'file_storage', 'messaging', 'analytics'];

  const filteredConnections = state.connections.filter(connection => {
    const matchesSearch = connection.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         connection.provider.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || connection.type === selectedType;
    return matchesSearch && matchesType;
  });

  if (showForm || isFormOpen) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="p-6">
          <div className="max-w-4xl mx-auto">
            <ConnectionForm
              connection={editingConnection || undefined}
              template={selectedTemplate || undefined}
              onSave={editingConnection ? handleUpdateConnection : handleCreateConnection}
              onCancel={() => {
                setShowForm(false);
                onFormClose();
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
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Connections
              </h1>
              <p className="text-default-600 mt-2 text-lg">Connect and manage your data sources and integrations</p>
            </div>
            <Button 
              color="primary" 
              size="lg"
              startContent={<Plus className="h-5 w-5" />}
              onPress={() => {
                setShowForm(true);
                onFormOpen();
              }}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
            >
              New Connection
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
                    <Plug className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Total Connections</p>
                    <p className="text-2xl font-bold text-foreground">{state.connections.length}</p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg">
                    <CheckCircle className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Active</p>
                    <p className="text-2xl font-bold text-foreground">
                      {state.connections.filter(c => c.status === 'active').length}
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 text-white shadow-lg">
                    <Clock className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Pending</p>
                    <p className="text-2xl font-bold text-foreground">
                      {state.connections.filter(c => c.status === 'pending').length}
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-red-500 to-pink-600 text-white shadow-lg">
                    <AlertCircle className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Errors</p>
                    <p className="text-2xl font-bold text-foreground">
                      {state.connections.filter(c => c.status === 'error').length}
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Tabs */}
          <div className="mb-8">
            <Tabs
              selectedKey={activeTab}
              onSelectionChange={(key) => setActiveTab(key as 'connections' | 'templates' | 'stats')}
              variant="underlined"
              color="primary"
              size="lg"
              classNames={{
                tabList: "bg-white/50 backdrop-blur-sm rounded-xl p-2 shadow-lg border border-white/20",
                tab: "data-[selected=true]:text-primary-600 font-semibold",
                cursor: "bg-gradient-to-r from-blue-500 to-purple-600",
              }}
            >
              <Tab
                key="connections"
                title={
                  <div className="flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    My Connections
                  </div>
                }
              />
              <Tab
                key="templates"
                title={
                  <div className="flex items-center gap-2">
                    <Grid3X3 className="h-4 w-4" />
                    Templates
                  </div>
                }
              />
              <Tab
                key="stats"
                title={
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Analytics
                  </div>
                }
              />
            </Tabs>
          </div>

          {/* Content Area */}
          {activeTab === 'connections' && (
            <div>
              {state.isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Spinner size="lg" color="primary" />
                </div>
              ) : (
                <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
                  <CardBody className="p-12 text-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-blue-500/10 to-purple-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                      <Plug className="h-10 w-10 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2 text-foreground">No connections found</h3>
                    <p className="text-default-600 mb-6 max-w-md mx-auto">
                      Get started by creating your first connection to integrate with external services and data sources.
                    </p>
                    <Button
                      color="primary"
                      size="lg"
                      startContent={<Plus className="h-5 w-5" />}
                      onPress={() => {
                        setShowForm(true);
                        onFormOpen();
                      }}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      Create Connection
                    </Button>
                  </CardBody>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg">
              <ConnectionTemplateGrid
                templates={state.templates}
                onSelectTemplate={handleSelectTemplate}
              />
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-lg">
              <ConnectionStatsGrid stats={stats} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
