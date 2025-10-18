import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardBody, Spinner, Alert } from '@heroui/react';
import { AlertCircle } from 'lucide-react';
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
      <Card>
        <CardBody className="text-center py-8">
          <p className="text-sm text-gray-500">Select a table to view its schema</p>
        </CardBody>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <CardBody className="flex items-center justify-center py-8">
          <Spinner size="sm" />
          <span className="text-sm text-gray-500 ml-2">Loading table schema...</span>
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardBody>
          <Alert
            color="danger"
            startContent={<AlertCircle className="h-4 w-4" />}
            title="Error"
            description={error}
          />
        </CardBody>
      </Card>
    );
  }

  if (!tableData) {
    return (
      <Card>
        <CardBody className="text-center py-8">
          <p className="text-sm text-gray-500">No table data available</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody className="gap-4">
        <div>
          <h3 className="font-semibold text-lg mb-2">{tableData.name}</h3>
          {tableData.schema && (
            <p className="text-xs text-gray-500">Schema: {tableData.schema}</p>
          )}
        </div>

        {/* Columns Table */}
        <div>
          <h4 className="font-semibold text-sm mb-2">Columns ({tableData.columns.length})</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left px-2 py-1 font-semibold">Name</th>
                  <th className="text-left px-2 py-1 font-semibold">Type</th>
                  <th className="text-left px-2 py-1 font-semibold">Nullable</th>
                  <th className="text-left px-2 py-1 font-semibold">Key</th>
                </tr>
              </thead>
              <tbody>
                {tableData.columns.map(col => (
                  <tr key={col.name} className="border-b hover:bg-gray-50">
                    <td className="px-2 py-1 font-mono text-xs">{col.name}</td>
                    <td className="px-2 py-1 text-xs text-gray-600">{col.type}</td>
                    <td className="px-2 py-1 text-xs">
                      {col.nullable ? '✓' : '✗'}
                    </td>
                    <td className="px-2 py-1 text-xs">
                      {col.isPrimaryKey && (
                        <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs">
                          PK
                        </span>
                      )}
                      {col.isForeignKey && (
                        <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded text-xs ml-1">
                          FK
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Primary Keys */}
        {tableData.primary_keys.length > 0 && (
          <div>
            <h4 className="font-semibold text-sm mb-2">Primary Keys</h4>
            <div className="flex flex-wrap gap-2">
              {tableData.primary_keys.map(pk => (
                <span
                  key={pk}
                  className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-mono"
                >
                  {pk}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Foreign Keys */}
        {tableData.foreign_keys.length > 0 && (
          <div>
            <h4 className="font-semibold text-sm mb-2">Foreign Keys</h4>
            <div className="space-y-2">
              {tableData.foreign_keys.map((fk, idx) => (
                <div
                  key={idx}
                  className="bg-green-50 border border-green-200 rounded p-2 text-xs"
                >
                  <p className="font-mono">
                    <span className="font-semibold">{fk.column}</span>
                    {' → '}
                    <span className="text-green-700">
                      {fk.referenced_table}.{fk.referenced_column}
                    </span>
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        {tableData.metadata && Object.keys(tableData.metadata).length > 0 && (
          <div>
            <h4 className="font-semibold text-sm mb-2">Metadata</h4>
            <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto max-h-32">
              {JSON.stringify(tableData.metadata, null, 2)}
            </pre>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default TableDiagram;

