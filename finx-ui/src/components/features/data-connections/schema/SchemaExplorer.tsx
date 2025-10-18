import React, { useState } from 'react';
import { Card, CardBody, Divider } from '@heroui/react';
import { SchemaSelector } from './SchemaSelector';
import { TableList } from './TableList';
import { TableDiagram } from './TableDiagram';

export interface SchemaExplorerProps {
  connectionId: string;
  connectionName?: string;
}

export const SchemaExplorer: React.FC<SchemaExplorerProps> = ({
  connectionId,
  connectionName = 'Connection',
}) => {
  const [selectedSchema, setSelectedSchema] = useState<string>('');
  const [selectedTable, setSelectedTable] = useState<string>('');

  return (
    <div className="w-full space-y-4">
      <Card>
        <CardBody>
          <h2 className="text-xl font-semibold mb-4">Schema Explorer</h2>
          <p className="text-sm text-gray-600">
            Exploring: <span className="font-semibold">{connectionName}</span>
          </p>
        </CardBody>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Schema Selector */}
        <div className="lg:col-span-1">
          <Card>
            <CardBody className="gap-4">
              <h3 className="font-semibold">Schemas</h3>
              <SchemaSelector
                connectionId={connectionId}
                selectedSchema={selectedSchema}
                onSchemaChange={setSelectedSchema}
              />
            </CardBody>
          </Card>
        </div>

        {/* Middle Column: Table List */}
        <div className="lg:col-span-1">
          {selectedSchema && (
            <TableList
              connectionId={connectionId}
              schemaName={selectedSchema}
              selectedTable={selectedTable}
              onTableSelect={setSelectedTable}
            />
          )}
        </div>

        {/* Right Column: Table Diagram */}
        <div className="lg:col-span-1">
          {selectedSchema && selectedTable && (
            <TableDiagram
              connectionId={connectionId}
              schemaName={selectedSchema}
              tableName={selectedTable}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default SchemaExplorer;

