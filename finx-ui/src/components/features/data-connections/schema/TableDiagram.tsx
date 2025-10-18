import React, { useState, useEffect } from 'react';
import { Card, CardBody, Spinner, Alert, Button, Chip } from '@heroui/react';
import { AlertCircle, Table as TableIcon, Key, Link2, Database, FileText, ArrowRight, Maximize2 } from 'lucide-react';
import { schemaAPI } from '@/lib/schemaAPI';
import { TableInfo } from '@/types/features/connections';

export interface TableDiagramProps {
  connectionId: string;
  schemaName: string;
  tableName?: string;
}

export const TableDiagram: React.FC<TableDiagramProps> = ({
  connectionId,
  schemaName,
  tableName,
}) => {
  const [tableData, setTableData] = useState<TableInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (tableName) {
      loadTableDetails();
    }
  }, [connectionId, schemaName, tableName]);

  const loadTableDetails = async () => {
    if (!tableName) return;

    setIsLoading(true);
    setError(null);
    try {
      const details = await schemaAPI.getTableDetails(
        connectionId,
        schemaName,
        tableName
      );
      setTableData(details);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load table details');
      console.error('Error loading table details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!tableName) {
    return (
      <Card className="h-full">
        <CardBody className="flex flex-col items-center justify-center py-16 text-center">
          <div className="p-6 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-4">
            <TableIcon className="h-16 w-16 text-gray-400" />
          </div>
          <p className="text-gray-600 font-medium text-lg">No Table Selected</p>
          <p className="text-sm text-gray-400 mt-2">Select a table to view its schema diagram</p>
        </CardBody>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardBody className="flex flex-col items-center justify-center py-16">
          <Spinner size="lg" color="primary" />
          <p className="text-gray-600 font-medium mt-4">Loading table schema...</p>
          <p className="text-sm text-gray-400 mt-1">Fetching structure for {tableName}</p>
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-full">
        <CardBody className="p-6">
          <Alert
            color="danger"
            variant="flat"
            startContent={<AlertCircle className="h-5 w-5" />}
            title="Error Loading Schema"
            description={error}
            className="bg-red-50 border border-red-200"
          />
        </CardBody>
      </Card>
    );
  }

  if (!tableData) {
    return (
      <Card className="h-full">
        <CardBody className="flex flex-col items-center justify-center py-16">
          <FileText className="h-16 w-16 text-gray-300 mb-4" />
          <p className="text-gray-500 font-medium">No schema data available</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardBody className="gap-6 p-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
              <Database className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {tableData.name}
              </h3>
              {tableData.schema && (
                <p className="text-sm text-gray-500 mt-1">
                  Schema: <span className="font-mono bg-gray-100 px-2 py-0.5 rounded">{tableData.schema}</span>
                </p>
              )}
              <div className="flex items-center gap-3 mt-2">
                <Chip size="sm" variant="flat" color="primary" startContent={<TableIcon className="h-3 w-3" />}>
                  {tableData.columns.length} columns
                </Chip>
                {tableData.primary_keys.length > 0 && (
                  <Chip size="sm" variant="flat" color="success" startContent={<Key className="h-3 w-3" />}>
                    {tableData.primary_keys.length} PK
                  </Chip>
                )}
                {tableData.foreign_keys.length > 0 && (
                  <Chip size="sm" variant="flat" color="warning" startContent={<Link2 className="h-3 w-3" />}>
                    {tableData.foreign_keys.length} FK
                  </Chip>
                )}
              </div>
            </div>
          </div>
          <Button
            isIconOnly
            size="sm"
            variant="flat"
            onPress={() => setIsExpanded(!isExpanded)}
          >
            <Maximize2 className="h-4 w-4" />
          </Button>
        </div>

        {/* Table Diagram Card */}
        <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-blue-50 rounded-xl p-6 border-2 border-blue-100 shadow-inner">
          <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200">
            {/* Table Header */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-3">
              <div className="flex items-center gap-2">
                <TableIcon className="h-5 w-5" />
                <span className="font-bold text-lg">{tableData.name}</span>
              </div>
            </div>

            {/* Columns List */}
            <div className="divide-y divide-gray-100">
              {tableData.columns.map((col, idx) => (
                <div
                  key={col.name}
                  className={`px-4 py-3 hover:bg-blue-50 transition-colors ${
                    idx === 0 ? 'bg-gray-50' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      {/* Column Icon */}
                      <div className={`p-1.5 rounded ${
                        col.isPrimaryKey 
                          ? 'bg-blue-100 text-blue-600' 
                          : col.isForeignKey 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-gray-100 text-gray-500'
                      }`}>
                        {col.isPrimaryKey ? (
                          <Key className="h-3 w-3" />
                        ) : col.isForeignKey ? (
                          <Link2 className="h-3 w-3" />
                        ) : (
                          <FileText className="h-3 w-3" />
                        )}
                      </div>

                      {/* Column Name */}
                      <span className={`font-mono text-sm ${
                        col.isPrimaryKey ? 'font-bold text-blue-700' : 'text-gray-800'
                      }`}>
                        {col.name}
                      </span>

                      {/* Badges */}
                      <div className="flex items-center gap-2">
                        {col.isPrimaryKey && (
                          <span className="bg-blue-500 text-white px-2 py-0.5 rounded text-xs font-bold">
                            PK
                          </span>
                        )}
                        {col.isForeignKey && (
                          <span className="bg-green-500 text-white px-2 py-0.5 rounded text-xs font-bold">
                            FK
                          </span>
                        )}
                        {!col.nullable && (
                          <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-semibold">
                            NOT NULL
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Column Type */}
                    <span className="text-xs font-semibold text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                      {col.type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Foreign Key Relationships */}
        {tableData.foreign_keys.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-bold text-sm text-gray-700 flex items-center gap-2">
              <Link2 className="h-4 w-4 text-green-600" />
              Foreign Key Relationships
            </h4>
            <div className="space-y-2">
              {tableData.foreign_keys.map((fk, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 flex-1">
                      <div className="p-2 rounded-lg bg-white shadow-sm">
                        <TableIcon className="h-4 w-4 text-blue-600" />
                      </div>
                      <span className="font-mono text-sm font-semibold text-gray-800">
                        {tableData.name}.{fk.column}
                      </span>
                    </div>

                    <ArrowRight className="h-5 w-5 text-green-600 flex-shrink-0" />

                    <div className="flex items-center gap-2 flex-1">
                      <div className="p-2 rounded-lg bg-white shadow-sm">
                        <Database className="h-4 w-4 text-purple-600" />
                      </div>
                      <span className="font-mono text-sm font-semibold text-green-700">
                        {fk.referenced_table}.{fk.referenced_column}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata Section */}
        {tableData.metadata && Object.keys(tableData.metadata).length > 0 && (
          <div className="space-y-3">
            <h4 className="font-bold text-sm text-gray-700 flex items-center gap-2">
              <FileText className="h-4 w-4 text-gray-600" />
              Additional Metadata
            </h4>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <pre className="text-xs font-mono overflow-auto max-h-48 text-gray-700">
                {JSON.stringify(tableData.metadata, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default TableDiagram;