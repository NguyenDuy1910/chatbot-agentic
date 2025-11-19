import React, { useState, useEffect } from 'react';
import { Button, Card, CardBody } from '@heroui/react';
import { ArrowLeft, Plus } from 'lucide-react';
import { PostgreSQLConnectionForm } from './forms/PostgreSQLConnectionForm';
import { AthenaConnectionForm } from './forms/AthenaConnectionForm';
import { DuckDBConnectionForm } from './forms/DuckDBConnectionForm';
import { CatalogSelector } from './schema/CatalogSelector';
import { SchemaExplorer } from './schema/SchemaExplorer';
import { AthenaSchemaExplorer } from './schema/AthenaSchemaExplorer';
import { type AthenaConnectionConfig } from '@/lib/athenaClient';
import { type StoredConnection } from '@/contexts/ConnectionContext';

interface ConnectionWorkflowWithTypeProps {
  onBack?: () => void;
  preSelectedDatabaseType?: string | null;
}

type DatabaseType = 'postgresql' | 'athena' | 'duckdb';

/**
 * Simplified workflow that goes directly to connection form based on pre-selected database type
 */
export const ConnectionWorkflowWithType: React.FC<ConnectionWorkflowWithTypeProps> = ({
  onBack,
  preSelectedDatabaseType,
}) => {
  const [step, setStep] = useState<'create' | 'catalog' | 'explore'>('create');
  const [selectedDatabase, setSelectedDatabase] = useState<DatabaseType | null>(
    (preSelectedDatabaseType as DatabaseType) || null
  );
  const [createdConnection, setCreatedConnection] = useState<{
    id?: string;
    name: string;
    config?: AthenaConnectionConfig;
  } | null>(null);
  const [selectedCatalog, setSelectedCatalog] = useState<string>('');

  const handleConnectionCreated = (connectionIdOrConfig: string | AthenaConnectionConfig) => {
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

  const handleCatalogSelected = (catalog: string) => {
    setSelectedCatalog(catalog);
    setStep('explore');
  };

  const handleBackToDashboard = () => {
    if (onBack) {
      onBack();
    }
  };

  // Step 1: Create Connection Form
  if (step === 'create' && selectedDatabase) {
    return (
      <div className="h-full p-6">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button
              isIconOnly
              variant="light"
              onClick={handleBackToDashboard}
              className="hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Create {selectedDatabase === 'postgresql' ? 'PostgreSQL' : selectedDatabase === 'athena' ? 'Athena' : 'DuckDB'} Connection
              </h1>
              <p className="text-gray-600 mt-2">
                Enter your connection details below
              </p>
            </div>
          </div>

          {/* Connection Form */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardBody className="p-8">
              {selectedDatabase === 'postgresql' && (
                <PostgreSQLConnectionForm
                  onSuccess={handleConnectionCreated}
                  onCancel={handleBackToDashboard}
                />
              )}
              {selectedDatabase === 'athena' && (
                <AthenaConnectionForm
                  onSuccess={handleConnectionCreated}
                  onCancel={handleBackToDashboard}
                />
              )}
              {selectedDatabase === 'duckdb' && (
                <DuckDBConnectionForm
                  onSuccess={handleConnectionCreated}
                  onCancel={handleBackToDashboard}
                />
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    );
  }

  // Step 2: Catalog Selection (Athena only)
  if (step === 'catalog' && createdConnection?.config) {
    return (
      <CatalogSelector
        connectionConfig={createdConnection.config}
        onCatalogSelect={handleCatalogSelected}
      />
    );
  }

  // Step 3: Schema Explorer
  if (step === 'explore') {
    if (selectedDatabase === 'athena' && createdConnection?.config && selectedCatalog) {
      return (
        <AthenaSchemaExplorer
          connectionConfig={createdConnection.config}
          catalogName={selectedCatalog}
        />
      );
    } else if (createdConnection?.id) {
      return (
        <SchemaExplorer
          connectionId={createdConnection.id}
        />
      );
    }
  }

  // Default fallback
  return (
    <div className="h-full p-6 flex items-center justify-center">
      <Card className="max-w-md">
        <CardBody className="p-8 text-center">
          <p className="text-gray-600 mb-4">Please select a database type from the modal</p>
          <Button color="primary" onClick={handleBackToDashboard}>
            Go Back
          </Button>
        </CardBody>
      </Card>
    </div>
  );
};
