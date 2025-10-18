import React, { useState } from 'react';
import { Card, CardBody, Button, Alert, Spinner, Chip } from '@heroui/react';
import { Database, Play, CheckCircle, AlertCircle } from 'lucide-react';
import { 
  useCurrentConnectionConfig, 
  useHasSavedConnections,
  useConnectionMetadata,
  useAthenaClient 
} from '@/hooks/useConnectionHooks';
import { useConnection } from '@/contexts/ConnectionContext';
import { createAthenaClient } from '@/lib/athenaClient';

/**
 * Example component showing how to reuse cached connections
 */
export const ReuseConnectionExample: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Various ways to access cached connections
  const hasSavedConnections = useHasSavedConnections();
  const currentConfig = useCurrentConnectionConfig();
  const metadata = useConnectionMetadata();
  const { config, isReady } = useAthenaClient();
  const { connections, currentConnection } = useConnection();

  const handleTestConnection = async () => {
    if (!currentConfig) {
      setError('No active connection found');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Reuse the cached connection config
      const client = createAthenaClient(currentConfig);
      
      // Test by listing catalogs
      const catalogs = await client.listCatalogs();
      
      setResult({
        success: true,
        message: 'Connection test successful!',
        catalogs: catalogs.map(c => c.name)
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection test failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardBody className="gap-4">
          <div className="flex items-center gap-2">
            <Database className="h-6 w-6 text-primary" />
            <h2 className="text-xl font-semibold">Reuse Cached Connection - Example</h2>
          </div>

          <Alert
            color="primary"
            title="Connection Reuse Pattern"
            description="This example demonstrates how to reuse cached connections in your components"
          />

          {/* Connection Status */}
          <div className="space-y-3">
            <h3 className="font-semibold">Connection Status</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="bg-gray-50">
                <CardBody>
                  <p className="text-sm font-medium text-gray-600">Has Saved Connections</p>
                  <Chip 
                    color={hasSavedConnections ? "success" : "default"}
                    variant="flat"
                    className="mt-2"
                  >
                    {hasSavedConnections ? 'Yes' : 'No'}
                  </Chip>
                </CardBody>
              </Card>

              <Card className="bg-gray-50">
                <CardBody>
                  <p className="text-sm font-medium text-gray-600">Total Saved</p>
                  <Chip color="primary" variant="flat" className="mt-2">
                    {connections.length}
                  </Chip>
                </CardBody>
              </Card>

              <Card className="bg-gray-50">
                <CardBody>
                  <p className="text-sm font-medium text-gray-600">Active Connection</p>
                  <Chip 
                    color={currentConnection ? "success" : "default"}
                    variant="flat"
                    className="mt-2"
                  >
                    {currentConnection?.name || 'None'}
                  </Chip>
                </CardBody>
              </Card>

              <Card className="bg-gray-50">
                <CardBody>
                  <p className="text-sm font-medium text-gray-600">Ready to Use</p>
                  <Chip 
                    color={isReady ? "success" : "warning"}
                    variant="flat"
                    className="mt-2"
                  >
                    {isReady ? 'Ready' : 'Not Ready'}
                  </Chip>
                </CardBody>
              </Card>
            </div>
          </div>

          {/* Connection Metadata */}
          {metadata.name && (
            <div className="space-y-2">
              <h3 className="font-semibold">Current Connection Metadata</h3>
              <Card className="bg-blue-50">
                <CardBody className="text-sm space-y-1">
                  <p><span className="font-medium">Name:</span> {metadata.name}</p>
                  <p><span className="font-medium">Type:</span> {metadata.type}</p>
                  {metadata.region && <p><span className="font-medium">Region:</span> {metadata.region}</p>}
                  {metadata.catalog && <p><span className="font-medium">Catalog:</span> {metadata.catalog}</p>}
                  {metadata.schema && <p><span className="font-medium">Schema:</span> {metadata.schema}</p>}
                  {metadata.lastUsed && (
                    <p><span className="font-medium">Last Used:</span> {new Date(metadata.lastUsed).toLocaleString()}</p>
                  )}
                </CardBody>
              </Card>
            </div>
          )}

          {/* Test Connection Button */}
          <div className="flex gap-3">
            <Button
              color="primary"
              size="lg"
              onClick={handleTestConnection}
              isLoading={isLoading}
              isDisabled={!isReady}
              startContent={!isLoading && <Play className="h-5 w-5" />}
            >
              Test Cached Connection
            </Button>
          </div>

          {/* Result */}
          {result && (
            <Alert
              color="success"
              startContent={<CheckCircle className="h-5 w-5" />}
              title={result.message}
              description={
                <div className="mt-2">
                  <p className="font-medium">Found Catalogs:</p>
                  <ul className="list-disc list-inside mt-1">
                    {result.catalogs.map((catalog: string) => (
                      <li key={catalog}>{catalog}</li>
                    ))}
                  </ul>
                </div>
              }
            />
          )}

          {error && (
            <Alert
              color="danger"
              startContent={<AlertCircle className="h-5 w-5" />}
              title="Error"
              description={error}
            />
          )}

          {/* Code Example */}
          <div className="space-y-2 mt-6">
            <h3 className="font-semibold">Code Example</h3>
            <Card className="bg-gray-900 text-white">
              <CardBody>
                <pre className="text-xs overflow-x-auto">
{`// Import the hooks
import { 
  useCurrentConnectionConfig,
  useAthenaClient 
} from '@/hooks/useConnectionHooks';
import { createAthenaClient } from '@/lib/athenaClient';

// In your component
const MyComponent = () => {
  // Get current connection config
  const currentConfig = useCurrentConnectionConfig();
  
  // Or use the helper hook
  const { config, isReady } = useAthenaClient();
  
  const handleQuery = async () => {
    if (!isReady || !config) return;
    
    // Reuse the cached connection
    const client = createAthenaClient(config);
    const catalogs = await client.listCatalogs();
    
    console.log('Catalogs:', catalogs);
  };
  
  return (
    <button onClick={handleQuery} disabled={!isReady}>
      Run Query
    </button>
  );
};`}
                </pre>
              </CardBody>
            </Card>
          </div>

          {/* Available Hooks */}
          <div className="space-y-2">
            <h3 className="font-semibold">Available Connection Hooks</h3>
            <Card className="bg-green-50">
              <CardBody className="text-sm space-y-2">
                <p>✅ <code className="bg-white px-2 py-0.5 rounded">useCurrentConnectionConfig()</code> - Get active connection config</p>
                <p>✅ <code className="bg-white px-2 py-0.5 rounded">useConnectionConfig(id)</code> - Get specific connection by ID</p>
                <p>✅ <code className="bg-white px-2 py-0.5 rounded">useHasSavedConnections()</code> - Check if has saved connections</p>
                <p>✅ <code className="bg-white px-2 py-0.5 rounded">useDefaultConnection()</code> - Get default connection</p>
                <p>✅ <code className="bg-white px-2 py-0.5 rounded">useConnectionsByType(type)</code> - Get connections by type</p>
                <p>✅ <code className="bg-white px-2 py-0.5 rounded">useAthenaClient()</code> - Quick access to Athena client</p>
                <p>✅ <code className="bg-white px-2 py-0.5 rounded">useConnectionMetadata(id?)</code> - Get connection metadata</p>
              </CardBody>
            </Card>
          </div>

          {!hasSavedConnections && (
            <Alert
              color="warning"
              startContent={<AlertCircle className="h-5 w-5" />}
              title="No Saved Connections"
              description="Please create and test a connection first. Go to Connections page to get started."
            />
          )}
        </CardBody>
      </Card>
    </div>
  );
};

export default ReuseConnectionExample;
