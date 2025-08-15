import React, { useState } from 'react';
import { DatabaseConnection, DatabaseType } from '@/types/database';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Textarea';
import { X, TestTube, Eye, EyeOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DatabaseConnectionFormProps {
  connection?: DatabaseConnection;
  onSave: (connection: Omit<DatabaseConnection, 'id' | 'createdAt' | 'updatedAt' | 'isConnected' | 'lastConnected'>) => void;
  onCancel: () => void;
  onTest?: (connectionData: any) => Promise<{ success: boolean; message: string }>;
  isLoading?: boolean;
}

export const DatabaseConnectionForm: React.FC<DatabaseConnectionFormProps> = ({
  connection,
  onSave,
  onCancel,
  onTest,
  isLoading = false
}) => {
  const [formData, setFormData] = useState({
    name: connection?.name || '',
    type: connection?.type || 'postgresql' as DatabaseType,
    host: connection?.host || 'localhost',
    port: connection?.port || 5432,
    database: connection?.database || '',
    username: connection?.username || '',
    password: connection?.password || '',
    schema: connection?.schema || '',
    connectionString: connection?.connectionString || '',
    isActive: connection?.isActive ?? true,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [useConnectionString, setUseConnectionString] = useState(!!connection?.connectionString);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [testing, setTesting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim() && (useConnectionString ? formData.connectionString.trim() : formData.database.trim())) {
      onSave(formData);
    }
  };

  const handleTest = async () => {
    if (!onTest) return;
    
    setTesting(true);
    setTestResult(null);
    
    try {
      const result = await onTest(formData);
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        message: error instanceof Error ? error.message : 'Connection test failed'
      });
    } finally {
      setTesting(false);
    }
  };

  const databaseTypes: { value: DatabaseType; label: string; defaultPort: number }[] = [
    { value: 'postgresql', label: 'PostgreSQL', defaultPort: 5432 },
    { value: 'mysql', label: 'MySQL', defaultPort: 3306 },
    { value: 'sqlite', label: 'SQLite', defaultPort: 0 },
    { value: 'mssql', label: 'SQL Server', defaultPort: 1433 },
    { value: 'oracle', label: 'Oracle', defaultPort: 1521 },
    { value: 'mongodb', label: 'MongoDB', defaultPort: 27017 },
    { value: 'redis', label: 'Redis', defaultPort: 6379 },
  ];

  const handleTypeChange = (type: DatabaseType) => {
    const dbType = databaseTypes.find(t => t.value === type);
    setFormData(prev => ({
      ...prev,
      type,
      port: dbType?.defaultPort || prev.port
    }));
  };

  return (
    <div className="bg-background border rounded-lg p-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">
          {connection ? 'Edit Database Connection' : 'New Database Connection'}
        </h2>
        <Button variant="ghost" size="icon" onClick={onCancel}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">
              Connection Name *
            </label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="My Database"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">
              Database Type *
            </label>
            <Select
              value={formData.type}
              onChange={(e) => handleTypeChange(e.target.value as DatabaseType)}
            >
              {databaseTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </Select>
          </div>
        </div>

        <div className="flex items-center gap-2 mb-4">
          <input
            type="checkbox"
            id="useConnectionString"
            checked={useConnectionString}
            onChange={(e) => setUseConnectionString(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="useConnectionString" className="text-sm font-medium">
            Use connection string instead of individual fields
          </label>
        </div>

        {useConnectionString ? (
          <div>
            <label className="text-sm font-medium mb-2 block">
              Connection String *
            </label>
            <Textarea
              value={formData.connectionString}
              onChange={(e) => setFormData(prev => ({ ...prev, connectionString: e.target.value }))}
              placeholder="postgresql://username:password@host:port/database"
              rows={3}
              required
            />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-2 block">
                  Host *
                </label>
                <Input
                  value={formData.host}
                  onChange={(e) => setFormData(prev => ({ ...prev, host: e.target.value }))}
                  placeholder="localhost"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Port *
                </label>
                <Input
                  type="number"
                  value={formData.port}
                  onChange={(e) => setFormData(prev => ({ ...prev, port: parseInt(e.target.value) || 5432 }))}
                  required
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                Database Name *
              </label>
              <Input
                value={formData.database}
                onChange={(e) => setFormData(prev => ({ ...prev, database: e.target.value }))}
                placeholder="my_database"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Username *
                </label>
                <Input
                  value={formData.username}
                  onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                  placeholder="username"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Password
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                    placeholder="password"
                    className="pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                Schema (Optional)
              </label>
              <Input
                value={formData.schema}
                onChange={(e) => setFormData(prev => ({ ...prev, schema: e.target.value }))}
                placeholder="public"
              />
            </div>
          </>
        )}

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="isActive"
            checked={formData.isActive}
            onChange={(e) => setFormData(prev => ({ ...prev, isActive: e.target.checked }))}
            className="rounded"
          />
          <label htmlFor="isActive" className="text-sm font-medium">
            Active connection
          </label>
        </div>

        {/* Test Connection */}
        {onTest && (
          <div className="border rounded-lg p-4 bg-muted/20">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium">Test Connection</h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleTest}
                disabled={testing}
              >
                <TestTube className="h-4 w-4 mr-2" />
                {testing ? 'Testing...' : 'Test'}
              </Button>
            </div>
            
            {testResult && (
              <div className={cn(
                'text-sm p-2 rounded',
                testResult.success 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : 'bg-red-50 text-red-800 border border-red-200'
              )}>
                {testResult.message}
              </div>
            )}
          </div>
        )}

        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : (connection ? 'Update' : 'Create')}
          </Button>
        </div>
      </form>
    </div>
  );
};
