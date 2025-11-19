import React, { useState } from 'react';
import { Card, CardBody, Button, Radio, RadioGroup, Alert, Divider } from '@heroui/react';
import { Database, Plus, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { useConnection } from '@/contexts/ConnectionContext';
import type { AthenaConnectionConfig } from '@/lib/athenaClient';

interface ConnectionSelectorProps {
  onSelectExisting?: (connectionId: string, config: AthenaConnectionConfig) => void;
  onCreateNew?: () => void;
  title?: string;
  description?: string;
}

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

export const ConnectionSelector: React.FC<ConnectionSelectorProps> = ({
  onSelectExisting,
  onCreateNew,
  title = 'Select Connection',
  description = 'Choose an existing connection or create a new one'
}) => {
  const { connections } = useConnection();
  const [selectedId, setSelectedId] = useState<string>('');
  const [mode, setMode] = useState<'existing' | 'new'>('existing');

  const handleContinue = () => {
    if (mode === 'new') {
      onCreateNew?.();
    } else if (mode === 'existing' && selectedId) {
      const connection = connections.find(c => c.id === selectedId);
      if (connection && onSelectExisting) {
        onSelectExisting(connection.id, connection.config as AthenaConnectionConfig);
      }
    }
  };

  const canContinue = mode === 'new' || (mode === 'existing' && selectedId);

  return (
    <Card className="w-full">
      <CardBody className="gap-6">
        <div className="flex items-center gap-2">
          <Database className="h-6 w-6 text-primary" />
          <div>
            <h3 className="text-xl font-semibold">{title}</h3>
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          </div>
        </div>

        <Divider />

        {connections.length > 0 ? (
          <>
            <RadioGroup
              label="Connection Options"
              value={mode}
              onValueChange={(value) => setMode(value as 'existing' | 'new')}
            >
              <Radio value="existing">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Use existing connection ({connections.length} available)</span>
                </div>
              </Radio>
              <Radio value="new">
                <div className="flex items-center gap-2">
                  <Plus className="h-4 w-4 text-blue-500" />
                  <span>Create new connection</span>
                </div>
              </Radio>
            </RadioGroup>

            {mode === 'existing' && (
              <div className="space-y-3 ml-6">
                <p className="text-sm text-gray-600 font-medium">Select a saved connection:</p>
                <RadioGroup
                  value={selectedId}
                  onValueChange={setSelectedId}
                  classNames={{
                    wrapper: "gap-3"
                  }}
                >
                  {connections.map((connection) => (
                    <Radio key={connection.id} value={connection.id}>
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{connection.name}</span>
                          {connection.isDefault && (
                            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                              Default
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          {connection.type.toUpperCase()} • 
                          {connection.metadata?.region && ` ${connection.metadata.region} • `}
                          {connection.metadata?.catalog && ` ${connection.metadata.catalog}`}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <Clock className="h-3 w-3" />
                          Used {formatTimeAgo(connection.lastUsed)}
                        </div>
                      </div>
                    </Radio>
                  ))}
                </RadioGroup>
              </div>
            )}

            {mode === 'new' && (
              <Alert
                color="primary"
                startContent={<Plus className="h-4 w-4" />}
                title="Create New Connection"
                description="You'll be guided through the connection setup process"
                className="ml-6"
              />
            )}
          </>
        ) : (
          <Alert
            color="warning"
            startContent={<AlertCircle className="h-4 w-4" />}
            title="No Saved Connections"
            description="You don't have any saved connections yet. Create your first connection to get started."
          />
        )}

        <Divider />

        <div className="flex gap-3 justify-end">
          <Button
            color="primary"
            size="lg"
            onClick={handleContinue}
            isDisabled={!canContinue}
            endContent={<CheckCircle className="h-4 w-4" />}
          >
            {mode === 'new' ? 'Create New' : 'Use Selected Connection'}
          </Button>
        </div>

        {connections.length > 0 && (
          <div className="text-xs text-gray-500 bg-blue-50 p-3 rounded-lg">
            <p className="font-semibold text-blue-900 mb-1">💡 Tip:</p>
            <p>Saved connections are stored in your session and automatically cleared when you logout for security.</p>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default ConnectionSelector;
