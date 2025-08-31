import React from 'react';
import { ConnectionDashboardStats } from '@/types/features/connections';
import { Card } from '@/components/shared/ui/Card';
import '@/styles/components/julius-ai-styles.css';
import { 
  Activity, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Zap,
  TrendingUp,
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
  Settings,
  Plug
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ConnectionStatsGridProps {
  stats: ConnectionDashboardStats | null;
}

export const ConnectionStatsGrid: React.FC<ConnectionStatsGridProps> = ({ stats }) => {
  if (!stats) {
    return (
      <div className="p-4 lg:p-6 h-full flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading statistics...</p>
        </div>
      </div>
    );
  }

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
  };

  const formatPercentage = (value: number) => {
    return `${Math.round(value)}%`;
  };

  const formatResponseTime = (ms: number) => {
    if (ms < 1000) {
      return `${Math.round(ms)}ms`;
    }
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="p-6 julius-content">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Connection Statistics</h2>
        <p className="text-sm text-gray-600">
          Overview of your connection health and performance metrics
        </p>
      </div>

      <div className="space-y-6">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Connections</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalConnections}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-green-600">{stats.activeConnections}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Errors</p>
                <p className="text-2xl font-bold text-red-600">{stats.errorConnections}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Uptime</p>
                <p className="text-2xl font-bold text-blue-600">{formatPercentage(stats.uptime)}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </Card>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Zap className="h-5 w-5" />
              <span>Performance</span>
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Average Response Time</span>
                <span className="font-medium">{formatResponseTime(stats.averageResponseTime)}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Recently Used (24h)</span>
                <span className="font-medium">{stats.recentlyUsed}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">System Uptime</span>
                <span className="font-medium text-green-600">{formatPercentage(stats.uptime)}</span>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Status Distribution</span>
            </h3>
            
            <div className="space-y-3">
              {Object.entries(stats.connectionsByStatus).map(([status, count]) => {
                const percentage = stats.totalConnections > 0 
                  ? (count / stats.totalConnections) * 100 
                  : 0;
                
                return (
                  <div key={status} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={cn(
                        "w-3 h-3 rounded-full",
                        getStatusColor(status).split(' ')[1]
                      )} />
                      <span className="text-sm capitalize">{status}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{count}</span>
                      <span className="text-xs text-gray-400">
                        ({formatPercentage(percentage)})
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>

        {/* Connection Types */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Connection Types</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Object.entries(stats.connectionsByType)
              .filter(([_, count]) => count > 0)
              .sort(([, a], [, b]) => b - a)
              .map(([type, count]) => {
                const percentage = stats.totalConnections > 0 
                  ? (count / stats.totalConnections) * 100 
                  : 0;
                
                return (
                  <div key={type} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0">
                      {getTypeIcon(type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 capitalize truncate">
                        {type.replace('_', ' ')}
                      </p>
                      <div className="flex items-center space-x-2">
                        <span className="text-lg font-bold text-gray-900">{count}</span>
                        <span className="text-xs text-gray-500">
                          ({formatPercentage(percentage)})
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
          
          {Object.values(stats.connectionsByType).every(count => count === 0) && (
            <div className="text-center py-8 text-gray-500">
              <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No connections configured yet</p>
            </div>
          )}
        </Card>

        {/* Health Summary */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <CheckCircle className="h-5 w-5" />
            <span>Health Summary</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <p className="text-2xl font-bold text-green-600">{stats.activeConnections}</p>
              <p className="text-sm text-gray-600">Healthy Connections</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-yellow-100 rounded-full flex items-center justify-center">
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
              <p className="text-2xl font-bold text-yellow-600">
                {stats.totalConnections - stats.activeConnections - stats.errorConnections}
              </p>
              <p className="text-sm text-gray-600">Pending/Inactive</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
              <p className="text-2xl font-bold text-red-600">{stats.errorConnections}</p>
              <p className="text-sm text-gray-600">Failed Connections</p>
            </div>
          </div>
          
          {stats.errorConnections > 0 && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="font-medium text-red-800">
                  {stats.errorConnections} connection{stats.errorConnections > 1 ? 's' : ''} need attention
                </span>
              </div>
              <p className="text-sm text-red-700 mt-1">
                Check the connections tab to diagnose and fix connection issues.
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
