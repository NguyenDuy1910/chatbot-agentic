import React, { useState, useEffect } from 'react';
import { Select, SelectItem, Spinner, Alert } from '@heroui/react';
import { AlertCircle } from 'lucide-react';
import { schemaAPI } from '@/lib/schemaAPI';

export interface SchemaSelectorProps {
  connectionId: string;
  selectedSchema?: string;
  onSchemaChange: (schema: string) => void;
}

export const SchemaSelector: React.FC<SchemaSelectorProps> = ({
  connectionId,
  selectedSchema,
  onSchemaChange,
}) => {
  const [schemas, setSchemas] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSchemas();
  }, [connectionId]);

  const loadSchemas = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const schemaList = await schemaAPI.getSchemas(connectionId);
      const schemaNames = schemaList.map(s => s.name);
      setSchemas(schemaNames);
      
      // Auto-select first schema if available
      if (schemaNames.length > 0 && !selectedSchema) {
        onSchemaChange(schemaNames[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schemas');
      console.error('Error loading schemas:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2">
        <Spinner size="sm" />
        <span className="text-sm text-gray-500">Loading schemas...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        color="danger"
        startContent={<AlertCircle className="h-4 w-4" />}
        title="Error"
        description={error}
      />
    );
  }

  if (schemas.length === 0) {
    return (
      <Alert
        color="warning"
        title="No Schemas"
        description="No schemas found in this connection"
      />
    );
  }

  return (
    <Select
      label="Select Schema"
      placeholder="Choose a schema"
      selectedKeys={selectedSchema ? [selectedSchema] : []}
      onChange={e => onSchemaChange(e.target.value)}
      className="w-full"
    >
      {schemas.map(schema => (
        <SelectItem key={schema}>
          {schema}
        </SelectItem>
      ))}
    </Select>
  );
};

export default SchemaSelector;

