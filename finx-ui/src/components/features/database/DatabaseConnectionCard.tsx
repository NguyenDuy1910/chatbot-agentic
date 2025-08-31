import React, { useState } from 'react';
import { DatabaseConnection } from '@/types/features/database';

import { Badge } from '@/components/shared/ui/Badge';
import { ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DatabaseConnectionModal } from './DatabaseConnectionModal';

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
  const [showModal, setShowModal] = useState(false);

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
    <>
      <div 
        className={cn(
          'bg-card border rounded-lg p-4 transition-all hover:shadow-md cursor-pointer',
          isSelected && 'ring-2 ring-primary ring-offset-2',
          !connection.isActive && 'opacity-60'
        )} 
        onClick={() => setShowModal(true)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">{getDatabaseIcon(connection.type)}</span>
            <div>
              <h3 className="font-medium text-card-foreground">
                {connection.name}
              </h3>
              <div className="text-xs text-muted-foreground flex items-center gap-2">
                <span>{connection.type.toUpperCase()}</span>
                <span>•</span>
                <span>{connection.database}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge 
              variant="outline" 
              className={cn('text-xs', getStatusColor(connection.isConnected, connection.isActive))}
            >
              {getStatusText(connection.isConnected, connection.isActive)}
            </Badge>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </div>
        </div>
      </div>

      {showModal && (
        <DatabaseConnectionModal
          connection={connection}
          onClose={() => setShowModal(false)}
          onEdit={onEdit}
          onDelete={onDelete}
          onTest={onTest}
          onSelect={onSelect}
        />
      )}
    </>
  );
};
