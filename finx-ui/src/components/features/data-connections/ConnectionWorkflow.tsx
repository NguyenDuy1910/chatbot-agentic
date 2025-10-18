import React, { useState } from 'react';
import { Card, CardBody, Button, Tabs, Tab } from '@heroui/react';
import { ArrowLeft, Plus } from 'lucide-react';
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
      <div className="h-full p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex items-center gap-4 mb-6">
            {onBack && (
              <Button
                isIconOnly
                variant="light"
                onClick={onBack}
                className="hover:bg-gray-100"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
            )}
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Connection Setup
              </h1>
              <p className="text-gray-600 mt-2">
                Use a saved connection or create a new one
              </p>
            </div>
          </div>

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
      <div className="h-full p-6">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            {onBack && (
              <Button
                isIconOnly
                variant="light"
                onClick={onBack}
                className="hover:bg-gray-100"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
            )}
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Create New Connection
              </h1>
              <p className="text-gray-600 mt-2">
                Select a database type to get started
              </p>
            </div>
          </div>

          {/* Database Type Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* PostgreSQL Card */}
            <Card
              isPressable
              onClick={() => handleDatabaseSelect('postgresql')}
              className="hover:shadow-2xl transition-all duration-300 cursor-pointer hover:scale-[1.03] border-2 border-transparent hover:border-blue-200"
            >
              <CardBody className="gap-5 p-8 flex flex-col items-center text-center min-h-[320px]">
                <div className="p-5 rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 shadow-lg">
                  <div className="text-6xl">🐘</div>
                </div>
                <div className="flex-1 flex flex-col justify-center space-y-3">
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    PostgreSQL
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed px-2">
                    Connect to PostgreSQL databases with full schema introspection and relationship mapping
                  </p>
                </div>
                <Button
                  color="primary"
                  size="lg"
                  startContent={<Plus className="h-5 w-5" />}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  Select PostgreSQL
                </Button>
              </CardBody>
            </Card>

            {/* Athena Card */}
            <Card
              isPressable
              onClick={() => handleDatabaseSelect('athena')}
              className="hover:shadow-2xl transition-all duration-300 cursor-pointer hover:scale-[1.03] border-2 border-transparent hover:border-orange-200"
            >
              <CardBody className="gap-5 p-8 flex flex-col items-center text-center min-h-[320px]">
                <div className="p-5 rounded-2xl bg-gradient-to-br from-orange-100 to-yellow-100 shadow-lg">
                  <div className="text-6xl">☁️</div>
                </div>
                <div className="flex-1 flex flex-col justify-center space-y-3">
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">
                    Amazon Athena
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed px-2">
                    Query data in S3 using Athena with environment-based authentication and serverless compute
                  </p>
                </div>
                <Button
                  color="warning"
                  size="lg"
                  startContent={<Plus className="h-5 w-5" />}
                  className="w-full bg-gradient-to-r from-orange-500 to-yellow-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  Select Athena
                </Button>
              </CardBody>
            </Card>

            {/* DuckDB Card */}
            <Card
              isPressable
              onClick={() => handleDatabaseSelect('duckdb')}
              className="hover:shadow-2xl transition-all duration-300 cursor-pointer hover:scale-[1.03] border-2 border-transparent hover:border-green-200"
            >
              <CardBody className="gap-5 p-8 flex flex-col items-center text-center min-h-[320px]">
                <div className="p-5 rounded-2xl bg-gradient-to-br from-green-100 to-emerald-100 shadow-lg">
                  <div className="text-6xl">🦆</div>
                </div>
                <div className="flex-1 flex flex-col justify-center space-y-3">
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                    DuckDB
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed px-2">
                    Lightweight analytical database for local or in-memory queries with blazing fast performance
                  </p>
                </div>
                <Button
                  color="success"
                  size="lg"
                  startContent={<Plus className="h-5 w-5" />}
                  className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  Select DuckDB
                </Button>
              </CardBody>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Create Connection
  if (step === 'create' && selectedDatabase) {
    return (
      <div className="h-full p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex items-center gap-4 mb-6">
            <Button
              isIconOnly
              variant="light"
              onClick={handleBackToSelect}
              className="hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Configure {selectedDatabase.charAt(0).toUpperCase() + selectedDatabase.slice(1)} Connection
              </h1>
              <p className="text-gray-600 mt-2">
                Enter your connection details
              </p>
            </div>
          </div>

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
      <div className="h-full p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex items-center gap-4 mb-6">
            <Button
              isIconOnly
              variant="light"
              onClick={handleBackToCreate}
              className="hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Select Catalog
              </h1>
              <p className="text-gray-600 mt-2">
                Choose a data catalog to explore
              </p>
            </div>
          </div>

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
      <div className="h-full p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="flex items-center gap-4 mb-6">
            <Button
              isIconOnly
              variant="light"
              onClick={selectedDatabase === 'athena' ? handleBackToCatalog : handleBackToCreate}
              className="hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Schema Explorer
              </h1>
              <p className="text-gray-600 mt-2">
                Browse and explore your database schema
              </p>
            </div>
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
      </div>
    );
  }

  return null;
};

export default ConnectionWorkflow;

