import React, { useState } from 'react';
import { Button, Input, Card, CardBody, Alert, Checkbox } from '@heroui/react';
import { AlertCircle, CheckCircle, Loader2, Info } from 'lucide-react';
import { connectionAPI } from '@/lib/connectionAPI';

export interface DuckDBConnectionFormProps {
  onSuccess?: (connectionId: string) => void;
  onCancel?: () => void;
}

export const DuckDBConnectionForm: React.FC<DuckDBConnectionFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    databasePath: ':memory:',
    readOnly: false,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<any>(null);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('Connection name is required');
      return false;
    }
    if (!formData.databasePath.trim()) {
      setError('Database path is required');
      return false;
    }
    return true;
  };

  const handleTestConnection = async () => {
    if (!validateForm()) return;

    setIsTesting(true);
    setError(null);
    try {
      const result = await connectionAPI.testConnection({
        connectionData: {
          name: formData.name,
          type: 'database',
          provider: 'duckdb',
          config: {
            customSettings: {
              database_path: formData.databasePath,
              read_only: formData.readOnly,
            },
          },
          credentials: {
            type: 'none',
          },
          healthCheck: {
            enabled: false,
            interval: 5,
          },
          isActive: true,
        },
      });

      setTestResult(result);
      if (result.success) {
        setSuccess('Connection test successful!');
      } else {
        setError(result.error || 'Connection test failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to test connection');
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await connectionAPI.createConnection({
        name: formData.name,
        description: formData.description,
        type: 'database',
        provider: 'duckdb',
        config: {
          customSettings: {
            database_path: formData.databasePath,
            read_only: formData.readOnly,
          },
        },
        credentials: {
          type: 'none',
        },
        healthCheck: {
          enabled: false,
          interval: 5,
        },
        isActive: true,
      });

      setSuccess('DuckDB connection created successfully!');
      setTimeout(() => {
        onSuccess?.(result.connection.id);
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create connection');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardBody className="gap-4">
        <h3 className="text-lg font-semibold">Create DuckDB Connection</h3>

        <Alert
          color="primary"
          startContent={<Info className="h-4 w-4" />}
          title="Database Path"
          description="Use ':memory:' for in-memory database, or provide a file path like '/path/to/database.duckdb'"
        />

        {error && (
          <Alert
            color="danger"
            startContent={<AlertCircle className="h-4 w-4" />}
            title="Error"
            description={error}
          />
        )}

        {success && (
          <Alert
            color="success"
            startContent={<CheckCircle className="h-4 w-4" />}
            title="Success"
            description={success}
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Connection Name"
            placeholder="e.g., My DuckDB"
            value={formData.name}
            onChange={e => handleInputChange('name', e.target.value)}
            isRequired
          />

          <Input
            label="Description"
            placeholder="Optional description"
            value={formData.description}
            onChange={e => handleInputChange('description', e.target.value)}
          />

          <Input
            label="Database Path"
            placeholder=":memory: or /path/to/database.duckdb"
            value={formData.databasePath}
            onChange={e => handleInputChange('databasePath', e.target.value)}
            isRequired
            description="Use ':memory:' for in-memory database"
          />

          <Checkbox
            isSelected={formData.readOnly}
            onChange={e => handleInputChange('readOnly', e.target.checked)}
          >
            Read-Only Mode
          </Checkbox>

          <div className="flex gap-2 pt-4">
            <Button
              color="primary"
              variant="bordered"
              onClick={handleTestConnection}
              isLoading={isTesting}
            >
              Test Connection
            </Button>

            <Button
              color="primary"
              type="submit"
              isLoading={isLoading}
            >
              Create Connection
            </Button>

            {onCancel && (
              <Button color="default" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>
        </form>

        {testResult && (
          <Card className="bg-gray-50">
            <CardBody className="text-sm">
              <p className="font-semibold">Test Result:</p>
              <p>{testResult.message}</p>
            </CardBody>
          </Card>
        )}
      </CardBody>
    </Card>
  );
};

export default DuckDBConnectionForm;

