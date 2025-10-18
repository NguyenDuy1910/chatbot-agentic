import React from 'react';
import { Card, CardBody, Button, Badge, Chip, Divider } from '@heroui/react';
import { Database, Trash2, CheckCircle, Clock, PlayCircle, ExternalLink, Network } from 'lucide-react';
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
  onExploreSchema?: (connection: StoredConnection) => void;
  showActions?: boolean;
  compact?: boolean;
}

export const SavedConnectionsList: React.FC<SavedConnectionsListProps> = ({
  onConnectionClick,
  onExploreSchema,
  showActions = true,
  compact = false
}) => {
  const { connections, currentConnection, setCurrentConnection, removeConnection } = useConnection();

  if (connections.length === 0) {
    return (
      <Card className="w-full border-2 border-dashed border-gray-300 bg-gradient-to-br from-gray-50 to-gray-100">
        <CardBody className="text-center py-12">
          <div className="p-4 rounded-xl bg-gradient-to-br from-blue-100 to-purple-100 w-fit mx-auto mb-4">
            <Database className="h-12 w-12 text-blue-600" />
          </div>
          <p className="text-lg font-semibold text-gray-700 mb-2">No saved connections</p>
          <p className="text-sm text-gray-500 max-w-md mx-auto">
            Test and connect to a data source to save it for this session. Your connections will appear here.
          </p>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
            <Database className="h-5 w-5 text-white" />
          </div>
          Session Connections
          <Chip size="sm" variant="flat" color="primary">
            {connections.length}
          </Chip>
        </h3>
      </div>

            <div className={`grid gap-4 ${compact ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'}`}>
        {connections.map((connection) => {
          const isActive = currentConnection?.id === connection.id;
          
          return (
            <Card 
              key={connection.id}
              className={`transition-all duration-300 min-h-[280px] flex flex-col ${
                isActive 
                  ? 'border-2 border-blue-500 shadow-lg shadow-blue-100 bg-gradient-to-br from-blue-50 to-purple-50' 
                  : 'hover:shadow-xl hover:scale-[1.02] hover:border-blue-200'
              }`}
            >
              <CardBody className="p-6 flex flex-col h-full">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`p-2 rounded-lg ${
                        isActive 
                          ? 'bg-gradient-to-br from-blue-500 to-purple-600' 
                          : 'bg-gradient-to-br from-gray-100 to-gray-200'
                      }`}>
                        <Database className={`h-4 w-4 ${isActive ? 'text-white' : 'text-gray-600'}`} />
                      </div>
                      <h4 className="font-semibold text-base truncate" title={connection.name}>
                        {connection.name}
                      </h4>
                    </div>

                    {/* Status Badges */}
                    <div className="flex items-center gap-2 flex-wrap">
                      {isActive && (
                        <Chip 
                          size="sm" 
                          className="bg-gradient-to-r from-green-500 to-emerald-600 text-white"
                          startContent={<CheckCircle className="h-3 w-3" />}
                        >
                          Active
                        </Chip>
                      )}
                      <Chip 
                        size="sm" 
                        className="bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                      >
                        {connection.type.toUpperCase()}
                      </Chip>
                      {connection.isDefault && (
                        <Chip size="sm" color="warning" variant="flat">
                          Default
                        </Chip>
                      )}
                    </div>
                  </div>

                  {/* Delete Button */}
                  {showActions && (
                    <Button
                      size="sm"
                      color="danger"
                      variant="light"
                      isIconOnly
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`Remove connection "${connection.name}"?`)) {
                          removeConnection(connection.id);
                        }
                      }}
                      className="hover:bg-red-100"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>

                {/* Connection Details */}
                {!compact && (
                  <div className="flex-1 space-y-2 text-sm">
                    {connection.metadata?.region && (
                      <div className="flex items-center gap-2 text-gray-600">
                        <span className="font-medium min-w-[60px]">Region:</span>
                        <Chip size="sm" variant="flat" className="font-mono text-xs">
                          {connection.metadata.region}
                        </Chip>
                      </div>
                    )}
                    
                    {connection.metadata?.catalog && (
                      <div className="flex items-center gap-2 text-gray-600">
                        <span className="font-medium min-w-[60px]">Catalog:</span>
                        <span className="font-mono text-xs truncate" title={connection.metadata.catalog}>
                          {connection.metadata.catalog}
                        </span>
                      </div>
                    )}
                    
                    {connection.metadata?.schema && (
                      <div className="flex items-center gap-2 text-gray-600">
                        <span className="font-medium min-w-[60px]">Schema:</span>
                        <span className="font-mono text-xs truncate" title={connection.metadata.schema}>
                          {connection.metadata.schema}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Footer with timestamp and actions */}
                <div className="mt-auto pt-4 space-y-3">
                  <Divider />
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-2">
                      <Clock className="h-3 w-3" />
                      <span>{formatTimeAgo(connection.lastUsed)}</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="grid grid-cols-2 gap-2">
                    {!isActive ? (
                      <Button
                        size="sm"
                        color="primary"
                        variant="flat"
                        startContent={<PlayCircle className="h-4 w-4" />}
                        onClick={(e) => {
                          e.stopPropagation();
                          setCurrentConnection(connection.id);
                          if (onConnectionClick) {
                            onConnectionClick(connection);
                          }
                        }}
                        className="w-full"
                      >
                        Use
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        color="success"
                        variant="flat"
                        startContent={<CheckCircle className="h-4 w-4" />}
                        isDisabled
                        className="w-full"
                      >
                        In Use
                      </Button>
                    )}
                    
                    <Button
                      size="sm"
                      color="secondary"
                      variant="flat"
                      startContent={<Network className="h-4 w-4" />}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onExploreSchema) {
                          onExploreSchema(connection);
                        }
                      }}
                      className="w-full"
                    >
                      Explore
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default SavedConnectionsList;
