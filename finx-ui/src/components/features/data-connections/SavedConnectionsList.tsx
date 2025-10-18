import React from 'react';
import { Card, CardBody, Button, Badge, Chip } from '@heroui/react';
import { Database, Trash2, CheckCircle, Clock, PlayCircle } from 'lucide-react';
import { useConnection, type StoredConnection } from '@/contexts/ConnectionContext';

// Simple time ago formatter
const formatTimeAgo = (date: Date): string => {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
  };

  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secondsInUnit);
    if (interval >= 1) {
      return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
    }
  }
  return 'just now';
};

interface SavedConnectionsListProps {
  onConnectionClick?: (connection: StoredConnection) => void;
  showActions?: boolean;
  compact?: boolean;
}

export const SavedConnectionsList: React.FC<SavedConnectionsListProps> = ({
  onConnectionClick,
  showActions = true,
  compact = false
}) => {
  const { connections, currentConnection, setCurrentConnection, removeConnection } = useConnection();

  const handleConnectionClick = (connection: StoredConnection) => {
    // Set as current connection
    setCurrentConnection(connection.id);
    
    // Call callback if provided
    if (onConnectionClick) {
      onConnectionClick(connection);
    }
  };

  if (connections.length === 0) {
    return (
      <Card className="w-full">
        <CardBody className="text-center py-8">
          <Database className="h-12 w-12 mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600">No saved connections</p>
          <p className="text-sm text-gray-500 mt-1">
            Test and connect to a data source to save it for this session
          </p>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Database className="h-5 w-5" />
          Saved Connections ({connections.length})
        </h3>
      </div>

      {connections.map((connection) => {
        const isActive = currentConnection?.id === connection.id;
        
        return (
          <Card 
            key={connection.id}
            isPressable={!isActive && !!onConnectionClick}
            onPress={() => !isActive && onConnectionClick && handleConnectionClick(connection)}
            className={`transition-all cursor-pointer hover:shadow-lg ${
              isActive ? 'border-2 border-primary bg-primary/5' : 'hover:border-primary/50'
            }`}
          >
            <CardBody className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {!isActive && onConnectionClick && (
                      <PlayCircle className="h-4 w-4 text-primary" />
                    )}
                    <h4 className="font-semibold">{connection.name}</h4>
                    {isActive && (
                      <Badge color="success" variant="flat" size="sm">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Active
                      </Badge>
                    )}
                    {connection.isDefault && (
                      <Chip size="sm" color="primary" variant="flat">
                        Default
                      </Chip>
                    )}
                  </div>

                  {!compact && (
                    <div className="text-sm text-gray-600 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Type:</span>
                        <Chip size="sm" variant="flat">
                          {connection.type.toUpperCase()}
                        </Chip>
                      </div>
                      
                      {connection.metadata?.region && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Region:</span>
                          <span>{connection.metadata.region}</span>
                        </div>
                      )}
                      
                      {connection.metadata?.catalog && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Catalog:</span>
                          <span>{connection.metadata.catalog}</span>
                        </div>
                      )}
                      
                      {connection.metadata?.schema && (
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Schema:</span>
                          <span>{connection.metadata.schema}</span>
                        </div>
                      )}

                      <div className="flex items-center gap-2 text-xs text-gray-500 mt-2">
                        <Clock className="h-3 w-3" />
                        Last used {formatTimeAgo(connection.lastUsed)}
                      </div>
                    </div>
                  )}

                  {!isActive && onConnectionClick && (
                    <p className="text-xs text-primary mt-2">
                      Click to use this connection →
                    </p>
                  )}
                </div>

                {showActions && (
                  <div className="flex flex-col gap-2 ml-4">
                    {!isActive && !onConnectionClick && (
                      <Button
                        size="sm"
                        color="primary"
                        variant="flat"
                        onClick={(e) => {
                          e.stopPropagation();
                          setCurrentConnection(connection.id);
                        }}
                      >
                        Use
                      </Button>
                    )}
                    <Button
                      size="sm"
                      color="danger"
                      variant="flat"
                      isIconOnly
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`Remove connection "${connection.name}"?`)) {
                          removeConnection(connection.id);
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardBody>
          </Card>
        );
      })}
    </div>
  );
};

export default SavedConnectionsList;
