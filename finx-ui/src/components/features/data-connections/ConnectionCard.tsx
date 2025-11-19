import React, { useState } from 'react';
import { Connection, ConnectionStatus, ConnectionTestResult } from '@/types/features/connections';
import { Button } from '@/components/shared/ui/Button';
import { Badge } from '@/components/shared/ui/Badge';
import { Card } from '@/components/shared/ui/Card';
import { 
  MoreVertical, 
  Play, 
  Edit, 
  Trash2, 
  Activity,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader2,
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
import { connectionAPI } from '@/lib/connectionAPI';

interface ConnectionCardProps {
  connection: Connection;
  onEdit: (connection: Connection) => void;
  onDelete: (connectionId: string) => void;
  onTest?: (connectionId: string) => void;
  onSelect?: (connection: Connection) => void;
  isSelected?: boolean;
  compact?: boolean;
}

export const ConnectionCard: React.FC<ConnectionCardProps> = ({
  connection,
  onEdit,
  onDelete,
  onTest,
  onSelect,
  isSelected = false,
  compact = false
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<ConnectionTestResult | null>(null);

  const getStatusColor = (status: ConnectionStatus) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'testing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: ConnectionStatus) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-3 w-3" />;
      case 'error':
        return <AlertCircle className="h-3 w-3" />;
      case 'testing':
        return <Loader2 className="h-3 w-3 animate-spin" />;
      default:
        return <Clock className="h-3 w-3" />;
    }
  };

  const getTypeIcon = (type: string) => {
    const iconClass = "h-4 w-4";
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

  const handleTest = async () => {
    if (!onTest) return;
    
    setIsTesting(true);
    setTestResult(null);
    
    try {
      const result = await connectionAPI.testExistingConnection(connection.id);
      setTestResult(result);
      onTest(connection.id);
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Test failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      });
    } finally {
      setIsTesting(false);
    }
  };

  const formatLastConnected = (date?: Date) => {
    if (!date) return 'Never';
    
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  if (compact) {
    return (
      <Card 
        className={cn(
          "p-3 cursor-pointer transition-all duration-200 hover:shadow-md",
          isSelected && "ring-2 ring-blue-500 bg-blue-50"
        )}
        onClick={() => onSelect?.(connection)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 min-w-0 flex-1">
            <div className="flex-shrink-0">
              {getTypeIcon(connection.type)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-900 truncate">
                {connection.name}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {connection.provider}
              </p>
            </div>
          </div>
          <Badge className={cn("text-xs", getStatusColor(connection.status))}>
            <span className="flex items-center space-x-1">
              {getStatusIcon(connection.status)}
              <span>{connection.status}</span>
            </span>
          </Badge>
        </div>
      </Card>
    );
  }

  return (
    <Card className={cn(
      "p-6 transition-all duration-200 hover:shadow-lg",
      isSelected && "ring-2 ring-blue-500 bg-blue-50"
    )}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4 flex-1">
          <div className="flex-shrink-0 p-2 bg-gray-100 rounded-lg">
            {getTypeIcon(connection.type)}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {connection.name}
              </h3>
              <Badge className={cn("text-xs", getStatusColor(connection.status))}>
                <span className="flex items-center space-x-1">
                  {getStatusIcon(connection.status)}
                  <span>{connection.status}</span>
                </span>
              </Badge>
            </div>
            
            <p className="text-sm text-gray-600 mb-2">
              {connection.description || `${connection.provider} ${connection.type} connection`}
            </p>
            
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span className="flex items-center space-x-1">
                <Activity className="h-3 w-3" />
                <span>Last: {formatLastConnected(connection.lastConnected)}</span>
              </span>
              
              {connection.errorCount > 0 && (
                <span className="flex items-center space-x-1 text-red-500">
                  <AlertCircle className="h-3 w-3" />
                  <span>{connection.errorCount} errors</span>
                </span>
              )}
              
              {connection.successCount > 0 && (
                <span className="flex items-center space-x-1 text-green-500">
                  <CheckCircle className="h-3 w-3" />
                  <span>{connection.successCount} success</span>
                </span>
              )}
            </div>
            
            {connection.tags && connection.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {connection.tags.slice(0, 3).map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {connection.tags.length > 3 && (
                  <Badge variant="secondary" className="text-xs">
                    +{connection.tags.length - 3}
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleTest}
            disabled={isTesting}
            className="flex items-center space-x-1"
          >
            {isTesting ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <Play className="h-3 w-3" />
            )}
            <span>Test</span>
          </Button>
          
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
            
            {isMenuOpen && (
              <div className="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg border z-10">
                <div className="py-1">
                  <button
                    onClick={() => {
                      onEdit(connection);
                      setIsMenuOpen(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <Edit className="h-4 w-4" />
                    <span>Edit</span>
                  </button>
                  <button
                    onClick={() => {
                      onDelete(connection.id);
                      setIsMenuOpen(false);
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {testResult && (
        <div className={cn(
          "mt-4 p-3 rounded-md text-sm",
          testResult.success 
            ? "bg-green-50 text-green-800 border border-green-200" 
            : "bg-red-50 text-red-800 border border-red-200"
        )}>
          <div className="flex items-center space-x-2">
            {testResult.success ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <span className="font-medium">{testResult.message}</span>
          </div>
          {testResult.responseTime && (
            <p className="mt-1 text-xs">
              Response time: {Math.round(testResult.responseTime * 1000)}ms
            </p>
          )}
          {testResult.error && (
            <p className="mt-1 text-xs opacity-75">
              {testResult.error}
            </p>
          )}
        </div>
      )}
    </Card>
  );
};
