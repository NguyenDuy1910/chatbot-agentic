import React from 'react';
import { DatabaseConnection } from '@/types/database';
import { Button } from '@/components/ui/Button';
import { 
  Edit3, 
  Trash2, 
  TestTube, 
  Activity,
  Clock,
  Server,
  HardDrive,
  X
} from 'lucide-react';

interface DatabaseConnectionModalProps {
  connection: DatabaseConnection;
  onClose: () => void;
  onEdit: (connection: DatabaseConnection) => void;
  onDelete: (id: string) => void;
  onTest: (id: string) => void;
  onSelect: (connection: DatabaseConnection) => void;
}

export const DatabaseConnectionModal: React.FC<DatabaseConnectionModalProps> = ({
  connection,
  onClose,
  onEdit,
  onDelete,
  onTest,
  onSelect,
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 relative">
        <Button
          variant="ghost"
          size="icon"
          className="absolute right-4 top-4"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>

        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-semibold">{connection.name}</h2>
            <div className={`px-2 py-1 rounded text-sm ${
              !connection.isActive ? 'bg-gray-100 text-gray-800' :
              connection.isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {!connection.isActive ? 'Inactive' : 
               connection.isConnected ? 'Connected' : 'Disconnected'}
            </div>
          </div>

          {/* Connection Details */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-1">Database Type</h3>
              <div className="flex items-center gap-2">
                <Server className="h-4 w-4" />
                {connection.type.toUpperCase()}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-1">Database Name</h3>
              <div className="flex items-center gap-2">
                <HardDrive className="h-4 w-4" />
                {connection.database}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-1">Host</h3>
              <p>{connection.host}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-1">Port</h3>
              <p>{connection.port}</p>
            </div>
          </div>

          {/* Metadata */}
          {connection.metadata && (
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-500 mb-3">Database Metadata</h3>
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <div className="text-sm text-gray-500">Tables</div>
                  <div className="text-xl font-semibold">{connection.metadata.tables.length}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Schemas</div>
                  <div className="text-xl font-semibold">{connection.metadata.schemas.length}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Version</div>
                  <div className="text-xl font-semibold">{connection.metadata.version || 'N/A'}</div>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-between items-center pt-4 border-t">
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => onTest(connection.id)}
              >
                <TestTube className="h-4 w-4 mr-2" />
                Test Connection
              </Button>
              <Button
                variant="outline"
                onClick={() => onEdit(connection)}
              >
                <Edit3 className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button
                variant="outline"
                className="text-red-600 hover:text-red-700"
                onClick={() => onDelete(connection.id)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </div>

            <Button
              variant="default"
              onClick={() => {
                onSelect(connection);
                onClose();
              }}
              disabled={!connection.isActive || !connection.isConnected}
            >
              <Activity className="h-4 w-4 mr-2" />
              Use for Queries
            </Button>
          </div>

          <div className="text-sm text-gray-500 flex justify-between items-center pt-2">
            {connection.lastConnected && (
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                Last connected: {connection.lastConnected.toLocaleDateString()}
              </span>
            )}
            <span>Updated: {connection.updatedAt.toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
