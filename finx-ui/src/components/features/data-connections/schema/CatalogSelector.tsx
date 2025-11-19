import React, { useState, useEffect } from 'react';
import { Card, CardBody, Button, Select, SelectItem, Alert, Spinner } from '@heroui/react';
import { Database, AlertCircle, CheckCircle, ChevronRight } from 'lucide-react';
import { createAthenaClient, type AthenaConnectionConfig } from '@/lib/athenaClient';
import { useConnection } from '@/contexts/ConnectionContext';

export interface CatalogSelectorProps {
  connectionConfig: AthenaConnectionConfig;
  connectionName?: string;
  onCatalogSelect?: (catalog: string) => void;
  onContinue?: () => void;
}

export const CatalogSelector: React.FC<CatalogSelectorProps> = ({
  connectionConfig,
  connectionName = 'Connection',
  onCatalogSelect,
  onContinue,
}) => {
  const [catalogs, setCatalogs] = useState<string[]>([]);
  const [selectedCatalog, setSelectedCatalog] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { addConnection, updateConnectionMetadata, currentConnection } = useConnection();

  useEffect(() => {
    loadCatalogs();
  }, []);

  const loadCatalogs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const client = createAthenaClient(connectionConfig);
      const catalogsList = await client.listCatalogs();
      const catalogNames = catalogsList.map(c => c.name);
      setCatalogs(catalogNames);
      
      // Auto-select first catalog if available (usually 'AwsDataCatalog')
      if (catalogNames.length > 0) {
        const defaultCatalog = catalogNames.find(c => c === 'AwsDataCatalog') || catalogNames[0];
        setSelectedCatalog(defaultCatalog);
        onCatalogSelect?.(defaultCatalog);
        
        // Save connection to session after successful catalog load
        if (!currentConnection || currentConnection.name !== connectionName) {
          addConnection({
            name: connectionName,
            type: 'athena',
            config: connectionConfig,
            isDefault: true,
            metadata: {
              catalog: defaultCatalog,
              region: connectionConfig.region
            }
          });
          console.log('✅ Connection saved to session:', connectionName);
        } else {
          // Update metadata if connection already exists
          updateConnectionMetadata(currentConnection.id, {
            catalog: defaultCatalog
          });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load catalogs');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCatalogChange = (value: string) => {
    setSelectedCatalog(value);
    onCatalogSelect?.(value);
    
    // Update catalog in connection metadata
    if (currentConnection) {
      updateConnectionMetadata(currentConnection.id, {
        catalog: value
      });
    }
  };

  const handleContinue = () => {
    if (selectedCatalog && onContinue) {
      onContinue();
    }
  };

  return (
    <Card className="w-full">
      <CardBody className="gap-4">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Select Catalog/Database</h3>
        </div>

        <p className="text-sm text-gray-600">
          Connected to: <span className="font-semibold">{connectionName}</span>
        </p>

        {error && (
          <Alert
            color="danger"
            startContent={<AlertCircle className="h-4 w-4" />}
            title="Error"
            description={error}
          />
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Spinner size="lg" />
            <span className="ml-3">Loading catalogs...</span>
          </div>
        ) : catalogs.length > 0 ? (
          <>
            <Alert
              color="success"
              startContent={<CheckCircle className="h-4 w-4" />}
              title="Catalogs Available"
              description={`Found ${catalogs.length} catalog(s) in this connection`}
            />

            <Select
              label="Select Catalog/Database"
              placeholder="Choose a catalog"
              selectedKeys={selectedCatalog ? [selectedCatalog] : []}
              onChange={e => handleCatalogChange(e.target.value)}
              className="max-w-md"
            >
              {catalogs.map(catalog => (
                <SelectItem key={catalog}>
                  {catalog}
                </SelectItem>
              ))}
            </Select>

            {selectedCatalog && (
              <div className="flex gap-2 pt-4">
                <Button
                  color="primary"
                  onClick={handleContinue}
                  endContent={<ChevronRight className="h-4 w-4" />}
                >
                  Continue to Schema Explorer
                </Button>
              </div>
            )}
          </>
        ) : (
          <Alert
            color="warning"
            startContent={<AlertCircle className="h-4 w-4" />}
            title="No Catalogs Found"
            description="No catalogs/databases were found for this connection."
          />
        )}

        <div className="text-xs text-gray-500 mt-4">
          <p>For Athena connections:</p>
          <ul className="list-disc list-inside ml-2 mt-1">
            <li>Catalogs represent AWS Glue Data Catalogs</li>
            <li>Each catalog contains databases and tables</li>
            <li>Select a catalog to explore its schemas and tables</li>
          </ul>
        </div>
      </CardBody>
    </Card>
  );
};

export default CatalogSelector;
