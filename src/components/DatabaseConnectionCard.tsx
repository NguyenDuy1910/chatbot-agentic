import React from 'react';
import { DatabaseConnection } from '@/types/database';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  Database, 
  Edit3, 
  Trash2, 
  TestTube, 
  Activity,
  Clock,
  Server,
  HardDrive
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface DatabaseConnectionCardProps {
  connection: DatabaseConnection;
  onEdit: (connection: DatabaseConnection) => void;
  onDelete: (id: string) => void;
  onTest: (id: string) => void;
  onSelect: (connection: DatabaseConnection) => void;
  isSelected?: boolean;
}

export const DatabaseConnectionCard: React.FC<DatabaseConnectionCardProps> = ({
  connection,
  onEdit,
  onDelete,
  onTest,
  onSelect,
  isSelected = false
}) => {
  const getStatusColor = (isConnected: boolean, isActive: boolean) => {
    if (!isActive) return 'bg-gray-100 text-gray-800';
    return isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  const getStatusText = (isConnected: boolean, isActive: boolean) => {
    if (!isActive) return 'Inactive';
    return isConnected ? 'Connected' : 'Disconnected';
  };

  const getDatabaseIcon = (type: string) => {
    const icons = {
      postgresql: '🐘',
      mysql: '🐬',
      sqlite: '📁',
      mssql: '🏢',
      oracle: '🔶',
      mongodb: '🍃',
      redis: '⚡',
    };
    return icons[type as keyof typeof icons] || '🗄️';
  };

  return (
    <div className={cn(
      'bg-card border rounded-lg p-4 space-y-3 transition-all hover:shadow-md cursor-pointer',
      isSelected && 'ring-2 ring-primary ring-offset-2',
      !connection.isActive && 'opacity-60'
    )} onClick={() => onSelect(connection)}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{getDatabaseIcon(connection.type)}</span>
            <h3 className="font-medium text-card-foreground truncate">
              {connection.name}
            </h3>
            <Badge 
              variant="outline" 
              className={cn('text-xs', getStatusColor(connection.isConnected, connection.isActive))}
            >
              {getStatusText(connection.isConnected, connection.isActive)}
            </Badge>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Server className="h-3 w-3" />
                {connection.type.toUpperCase()}
              </span>
              <span className="flex items-center gap-1">
                <HardDrive className="h-3 w-3" />
                {connection.database}
              </span>
            </div>
            
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span>
                {connection.host}:{connection.port}
              </span>
              {connection.lastConnected && (
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Last: {connection.lastConnected.toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-1 ml-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation();
              onTest(connection.id);
            }}
            title="Test connection"
          >
            <TestTube className="h-3 w-3" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(connection);
            }}
            title="Edit connection"
          >
            <Edit3 className="h-3 w-3" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-destructive hover:text-destructive"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(connection.id);
            }}
            title="Delete connection"
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Metadata Summary */}
      {connection.metadata && (
        <div className="border-t pt-3">
          <div className="grid grid-cols-3 gap-4 text-xs">
            <div className="text-center">
              <div className="font-medium text-muted-foreground">Tables</div>
              <div className="text-lg font-semibold">{connection.metadata.tables.length}</div>
            </div>
            <div className="text-center">
              <div className="font-medium text-muted-foreground">Schemas</div>
              <div className="text-lg font-semibold">{connection.metadata.schemas.length}</div>
            </div>
            <div className="text-center">
              <div className="font-medium text-muted-foreground">Version</div>
              <div className="text-sm font-medium truncate">{connection.metadata.version || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="flex justify-between items-center pt-2 border-t">
        <Button
          variant="outline"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onSelect(connection);
          }}
          disabled={!connection.isActive || !connection.isConnected}
        >
          <Activity className="h-3 w-3 mr-1" />
          Use for Queries
        </Button>
        
        <div className="text-xs text-muted-foreground">
          Updated {connection.updatedAt.toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};
