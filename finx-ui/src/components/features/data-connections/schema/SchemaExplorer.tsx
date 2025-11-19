import React, { useState } from 'react';
import { Card, CardBody, Button, ButtonGroup } from '@heroui/react';
import { List, Network, Table as TableIcon } from 'lucide-react';
import { SchemaSelector } from './SchemaSelector';
import { TableList } from './TableList';
import { TableDiagram } from './TableDiagram';
import { SchemaRelationshipDiagram } from './SchemaRelationshipDiagram';

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
  const [viewMode, setViewMode] = useState<'list' | 'diagram'>('list');
  const [tables, setTables] = useState<string[]>([]);

  return (
    <div className="w-full space-y-4">
      {/* Header Card */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-100">
        <CardBody className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                Schema Explorer
              </h2>
              <p className="text-sm text-gray-600">
                Exploring: <span className="font-semibold text-gray-800">{connectionName}</span>
              </p>
            </div>

            {/* View Mode Toggle */}
            {selectedSchema && tables.length > 0 && (
              <ButtonGroup variant="flat">
                <Button
                  size="sm"
                  color={viewMode === 'list' ? 'primary' : 'default'}
                  startContent={<List className="h-4 w-4" />}
                  onPress={() => setViewMode('list')}
                >
                  List View
                </Button>
                <Button
                  size="sm"
                  color={viewMode === 'diagram' ? 'primary' : 'default'}
                  startContent={<Network className="h-4 w-4" />}
                  onPress={() => setViewMode('diagram')}
                >
                  Diagram View
                </Button>
              </ButtonGroup>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Diagram View - Full Width */}
      {viewMode === 'diagram' && selectedSchema && tables.length > 0 ? (
        <SchemaRelationshipDiagram
          connectionId={connectionId}
          schemaName={selectedSchema}
          tables={tables}
        />
      ) : (
        /* List View - 3 Column Layout */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Column: Schema Selector */}
          <div className="lg:col-span-1">
            <Card className="h-full shadow-lg hover:shadow-xl transition-shadow">
              <CardBody className="gap-4 p-6">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
                    <TableIcon className="h-5 w-5" />
                  </div>
                  <h3 className="font-bold text-gray-800">Schemas</h3>
                </div>
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
                onTablesLoaded={setTables}
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
      )}
    </div>
  );
};

export default SchemaExplorer;

