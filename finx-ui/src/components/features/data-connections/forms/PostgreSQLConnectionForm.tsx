import React, { useState } from 'react';
import { Button, Input, Card, CardBody, Select, SelectItem, Alert } from '@heroui/react';
import { AlertCircle, CheckCircle, Loader2, Eye, EyeOff } from 'lucide-react';
import { connectionAPI } from '@/lib/connectionAPI';

export interface PostgreSQLConnectionFormProps {
  onSuccess?: (connectionId: string) => void;
  onCancel?: () => void;
}

export const PostgreSQLConnectionForm: React.FC<PostgreSQLConnectionFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    host: 'localhost',
    port: 5432,
    database: '',
    username: '',
    password: '',
    sslMode: 'prefer',
  });

  const [showPassword, setShowPassword] = useState(false);
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
    if (!formData.host.trim()) {
      setError('Host is required');
      return false;
    }
    if (!formData.database.trim()) {
      setError('Database name is required');
      return false;
    }
    if (!formData.username.trim()) {
      setError('Username is required');
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
          provider: 'postgresql',
          config: {
            customSettings: {
              host: formData.host,
              port: formData.port,
              sslmode: formData.sslMode,
            },
          },
          credentials: {
            type: 'basic_auth',
            username: formData.username,
            password: formData.password,
            additionalFields: {
              database: formData.database,
            },
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
        provider: 'postgresql',
        config: {
          customSettings: {
            host: formData.host,
            port: formData.port,
            sslmode: formData.sslMode,
          },
        },
        credentials: {
          type: 'basic_auth',
          username: formData.username,
          password: formData.password,
          additionalFields: {
            database: formData.database,
          },
        },
        healthCheck: {
          enabled: false,
          interval: 5,
        },
        isActive: true,
      });

      setSuccess('PostgreSQL connection created successfully!');
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
        <h3 className="text-lg font-semibold">Create PostgreSQL Connection</h3>

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
            placeholder="e.g., My PostgreSQL DB"
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

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Host"
              placeholder="localhost"
              value={formData.host}
              onChange={e => handleInputChange('host', e.target.value)}
              isRequired
            />

            <Input
              label="Port"
              type="number"
              placeholder="5432"
              value={formData.port.toString()}
              onChange={e => handleInputChange('port', parseInt(e.target.value))}
              isRequired
            />
          </div>

          <Input
            label="Database"
            placeholder="database_name"
            value={formData.database}
            onChange={e => handleInputChange('database', e.target.value)}
            isRequired
          />

          <Input
            label="Username"
            placeholder="postgres"
            value={formData.username}
            onChange={e => handleInputChange('username', e.target.value)}
            isRequired
          />

          <Input
            label="Password"
            type={showPassword ? 'text' : 'password'}
            placeholder="••••••••"
            value={formData.password}
            onChange={e => handleInputChange('password', e.target.value)}
            endContent={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="focus:outline-none"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4 text-gray-400" />
                ) : (
                  <Eye className="h-4 w-4 text-gray-400" />
                )}
              </button>
            }
          />

          <Select
            label="SSL Mode"
            selectedKeys={[formData.sslMode]}
            onChange={e => handleInputChange('sslMode', e.target.value)}
          >
            <SelectItem key="disable">
              Disable
            </SelectItem>
            <SelectItem key="allow">
              Allow
            </SelectItem>
            <SelectItem key="prefer">
              Prefer
            </SelectItem>
            <SelectItem key="require">
              Require
            </SelectItem>
          </Select>

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

export default PostgreSQLConnectionForm;

