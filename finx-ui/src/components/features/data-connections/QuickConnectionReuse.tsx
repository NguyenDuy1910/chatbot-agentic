import React, { useState } from 'react';
import { Card, CardBody, Button, Alert } from '@heroui/react';
import { ArrowLeft, Database } from 'lucide-react';
import { CatalogSelector } from './schema/CatalogSelector';
import { AthenaSchemaExplorer } from './schema/AthenaSchemaExplorer';
import type { StoredConnection } from '@/contexts/ConnectionContext';
import type { AthenaConnectionConfig } from '@/lib/athenaClient';

interface QuickConnectionReuseProps {
  connection: StoredConnection;
  onBack?: () => void;
}

/**
 * Component to quickly reuse a saved connection
 * Skips the connection form and goes straight to catalog/schema selection
 */
export const QuickConnectionReuse: React.FC<QuickConnectionReuseProps> = ({
  connection,
  onBack
}) => {
  const [step, setStep] = useState<'catalog' | 'explore'>('catalog');
  const [selectedCatalog, setSelectedCatalog] = useState<string>(
    connection.metadata?.catalog || ''
  );

  const handleCatalogSelect = (catalog: string) => {
    setSelectedCatalog(catalog);
  };

  const handleContinue = () => {
    if (selectedCatalog) {
      setStep('explore');
    }
  };

  // Catalog Selection Step
  if (step === 'catalog') {
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
          <div>
            <h2 className="text-2xl font-bold">Using: {connection.name}</h2>
            <p className="text-sm text-gray-600">
              Connection reused from session - Skip to catalog selection
            </p>
          </div>
        </div>

        <Alert
          color="success"
          title="Connection Ready"
          description="This connection is already configured and tested. Select a catalog to continue."
          className="mb-4"
        />

        <div className="max-w-2xl">
          <CatalogSelector
            connectionConfig={connection.config as AthenaConnectionConfig}
            connectionName={connection.name}
            onCatalogSelect={handleCatalogSelect}
            onContinue={handleContinue}
          />
        </div>
      </div>
    );
  }

  // Schema Explorer Step
  if (step === 'explore') {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Button
            isIconOnly
            variant="light"
            onClick={() => setStep('catalog')}
            startContent={<ArrowLeft className="h-4 w-4" />}
          />
          <div>
            <h2 className="text-2xl font-bold">Schema Explorer</h2>
            <p className="text-sm text-gray-600">
              {connection.name} • {selectedCatalog}
            </p>
          </div>
        </div>

        <AthenaSchemaExplorer
          connectionConfig={connection.config as AthenaConnectionConfig}
          connectionName={connection.name}
          catalogName={selectedCatalog}
        />
      </div>
    );
  }

  return null;
};

export default QuickConnectionReuse;
