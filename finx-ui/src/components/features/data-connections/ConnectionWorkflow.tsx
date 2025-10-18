import React, { useState } from 'react';
import { Card, CardBody, Button, Tabs, Tab } from '@heroui/react';
import { ArrowLeft, Plus } from 'lucide-react';
import { Connection } from '@/types/features/connections';
import { PostgreSQLConnectionForm } from './forms/PostgreSQLConnectionForm';
import { AthenaConnectionForm } from './forms/AthenaConnectionForm';
import { DuckDBConnectionForm } from './forms/DuckDBConnectionForm';
import { CatalogSelector } from './schema/CatalogSelector';
import { SchemaExplorer } from './schema/SchemaExplorer';
import { AthenaSchemaExplorer } from './schema/AthenaSchemaExplorer';
import { ConnectionSelector } from './ConnectionSelector';
import { type AthenaConnectionConfig } from '@/lib/athenaClient';
import { useHasSavedConnections } from '@/hooks/useConnectionHooks';
import { type StoredConnection } from '@/contexts/ConnectionContext';

export interface ConnectionWorkflowProps {
  onBack?: () => void;
  reuseConnection?: StoredConnection;  // If provided, skip to catalog selection with this connection
  forceNew?: boolean;  // If true, skip connection selector and force creating new
}

type DatabaseType = 'postgresql' | 'athena' | 'duckdb';

export const ConnectionWorkflow: React.FC<ConnectionWorkflowProps> = ({ 
  onBack, 
  reuseConnection,
  forceNew = false 
}) => {
  // Determine initial step based on props
  const getInitialStep = () => {
    if (reuseConnection) return 'catalog';  // Reusing -> go to catalog
    if (forceNew) return 'select';  // Force new -> skip to database selection
    return 'choose';  // Default -> show connection chooser
  };

  const [step, setStep] = useState<'choose' | 'select' | 'create' | 'catalog' | 'explore'>(
    getInitialStep()
  );
  const [selectedDatabase, setSelectedDatabase] = useState<DatabaseType | null>(
    reuseConnection ? 'athena' : null
  );
  const [createdConnection, setCreatedConnection] = useState<{
    id?: string;
    name: string;
    config?: AthenaConnectionConfig;
  } | null>(
    reuseConnection ? {
      id: reuseConnection.id,
      name: reuseConnection.name,
      config: reuseConnection.config as AthenaConnectionConfig
    } : null
  );
  const [selectedCatalog, setSelectedCatalog] = useState<string>('');
  const hasSavedConnections = useHasSavedConnections();

  const handleDatabaseSelect = (db: DatabaseType) => {
    setSelectedDatabase(db);
    setStep('create');
  };

  const handleConnectionCreated = (connectionIdOrConfig: string | AthenaConnectionConfig) => {
    // For Athena, we receive the config; for others, we receive connection ID
    if (selectedDatabase === 'athena' && typeof connectionIdOrConfig !== 'string') {
      setCreatedConnection({
        name: 'Athena Connection',
        config: connectionIdOrConfig as AthenaConnectionConfig,
      });
      setStep('catalog');
    } else {
      setCreatedConnection({
        id: connectionIdOrConfig as string,
        name: `${selectedDatabase} Connection`,
      });
      setStep('explore');
    }
  };

  const handleUseExisting = (connectionId: string, config: AthenaConnectionConfig) => {
    // Use existing connection - go straight to catalog selection
    setCreatedConnection({
      id: connectionId,
      name: 'Existing Connection',
      config: config
    });
    setSelectedDatabase('athena');
    setStep('catalog');
  };

  const handleCreateNew = () => {
    setStep('select');
  };

  const handleBackToChoose = () => {
    setStep('choose');
    setSelectedDatabase(null);
    setCreatedConnection(null);
    setSelectedCatalog('');
  };

  const handleBackToSelect = () => {
    setStep('select');
    setSelectedDatabase(null);
    setCreatedConnection(null);
    setSelectedCatalog('');
  };

  const handleBackToCreate = () => {
    setStep('create');
    setCreatedConnection(null);
    setSelectedCatalog('');
  };

  const handleBackToCatalog = () => {
    setStep('catalog');
    setSelectedCatalog('');
  };

  const handleCatalogSelected = (catalog: string) => {
    setSelectedCatalog(catalog);
  };

  const handleContinueToExplorer = () => {
    if (selectedCatalog) {
      setStep('explore');
    }
  };

  // Step 0: Choose between existing or new (if has saved connections AND not forced new)
  if (step === 'choose' && hasSavedConnections && !forceNew) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          {onBack && (
            <Button
              isIconOnly
              variant="light"
              onClick={onBack}
              startContent={<ArrowLeft className="h-4 w-4" />}
            />
          )}
          <h2 className="text-2xl font-bold">Connection Setup</h2>
        </div>

        <div className="max-w-2xl">
          <ConnectionSelector
            onSelectExisting={handleUseExisting}
            onCreateNew={handleCreateNew}
            title="Choose Connection"
            description="Use a saved connection from your session or create a new one"
          />
        </div>
      </div>
    );
  }

  // Step 1: Select Database Type
  if (step === 'select') {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Button
            isIconOnly
            variant="light"
            onClick={hasSavedConnections ? handleBackToChoose : (onBack || undefined)}
            startContent={<ArrowLeft className="h-4 w-4" />}
          />
          <h2 className="text-2xl font-bold">Create New Connection</h2>
        </div>

        <p className="text-gray-600 mb-6">
          Select a database type to create a new connection
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* PostgreSQL Card */}
          <Card
            isPressable
            onClick={() => handleDatabaseSelect('postgresql')}
            className="hover:shadow-lg transition-all cursor-pointer"
          >
            <CardBody className="gap-4 p-6">
              <div className="text-4xl">🐘</div>
              <h3 className="text-lg font-semibold">PostgreSQL</h3>
              <p className="text-sm text-gray-600">
                Connect to PostgreSQL databases with full schema introspection
              </p>
              <Button
                color="primary"
                size="sm"
                startContent={<Plus className="h-4 w-4" />}
              >
                Create Connection
              </Button>
            </CardBody>
          </Card>

          {/* Athena Card */}
          <Card
            isPressable
            onClick={() => handleDatabaseSelect('athena')}
            className="hover:shadow-lg transition-all cursor-pointer"
          >
            <CardBody className="gap-4 p-6">
              <div className="text-4xl">☁️</div>
              <h3 className="text-lg font-semibold">Amazon Athena</h3>
              <p className="text-sm text-gray-600">
                Query data in S3 using Athena with environment-based auth
              </p>
              <Button
                color="primary"
                size="sm"
                startContent={<Plus className="h-4 w-4" />}
              >
                Create Connection
              </Button>
            </CardBody>
          </Card>

          {/* DuckDB Card */}
          <Card
            isPressable
            onClick={() => handleDatabaseSelect('duckdb')}
            className="hover:shadow-lg transition-all cursor-pointer"
          >
            <CardBody className="gap-4 p-6">
              <div className="text-4xl">🦆</div>
              <h3 className="text-lg font-semibold">DuckDB</h3>
              <p className="text-sm text-gray-600">
                Lightweight analytical database for local or in-memory queries
              </p>
              <Button
                color="primary"
                size="sm"
                startContent={<Plus className="h-4 w-4" />}
              >
                Create Connection
              </Button>
            </CardBody>
          </Card>
        </div>
      </div>
    );
  }

  // Step 2: Create Connection
  if (step === 'create' && selectedDatabase) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Button
            isIconOnly
            variant="light"
            onClick={handleBackToSelect}
            startContent={<ArrowLeft className="h-4 w-4" />}
          />
          <h2 className="text-2xl font-bold">Create {selectedDatabase} Connection</h2>
        </div>

        <div className="max-w-2xl">
          {selectedDatabase === 'postgresql' && (
            <PostgreSQLConnectionForm
              onSuccess={handleConnectionCreated}
              onCancel={handleBackToSelect}
            />
          )}

          {selectedDatabase === 'athena' && (
            <AthenaConnectionForm
              onSuccess={handleConnectionCreated}
              onCancel={handleBackToSelect}
            />
          )}

          {selectedDatabase === 'duckdb' && (
            <DuckDBConnectionForm
              onSuccess={handleConnectionCreated}
              onCancel={handleBackToSelect}
            />
          )}
        </div>
      </div>
    );
  }

  // Step 3: Select Catalog (for Athena)
  if (step === 'catalog' && createdConnection && createdConnection.config) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Button
            isIconOnly
            variant="light"
            onClick={handleBackToCreate}
            startContent={<ArrowLeft className="h-4 w-4" />}
          />
          <h2 className="text-2xl font-bold">Select Catalog</h2>
        </div>

        <div className="max-w-2xl">
          <CatalogSelector
            connectionConfig={createdConnection.config}
            connectionName={createdConnection.name}
            onCatalogSelect={handleCatalogSelected}
            onContinue={handleContinueToExplorer}
          />
        </div>
      </div>
    );
  }

  // Step 4: Explore Schema
  if (step === 'explore' && createdConnection) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Button
            isIconOnly
            variant="light"
            onClick={selectedDatabase === 'athena' ? handleBackToCatalog : handleBackToCreate}
            startContent={<ArrowLeft className="h-4 w-4" />}
          />
          <h2 className="text-2xl font-bold">Schema Explorer</h2>
        </div>

        {selectedDatabase === 'athena' && createdConnection.config ? (
          <AthenaSchemaExplorer
            connectionConfig={createdConnection.config}
            connectionName={createdConnection.name}
            catalogName={selectedCatalog}
          />
        ) : createdConnection.id ? (
          <SchemaExplorer
            connectionId={createdConnection.id}
            connectionName={createdConnection.name}
          />
        ) : null}
      </div>
    );
  }

  return null;
};

export default ConnectionWorkflow;

