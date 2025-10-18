import React, { useState, useEffect } from 'react';
import { Card, CardBody, Spinner, Alert, Button, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure, Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/react';
import { AlertCircle, Table as TableIcon, RefreshCw, Eye, Database } from 'lucide-react';
import { schemaAPI } from '@/lib/schemaAPI';

export interface TableListProps {
  connectionId: string;
  schemaName: string;
  selectedTable?: string;
  onTableSelect: (tableName: string) => void;
  onTablesLoaded?: (tables: string[]) => void;
}

interface TablePreviewData {
  columns: string[];
  rows: any[][];
}

export const TableList: React.FC<TableListProps> = ({
  connectionId,
  schemaName,
  selectedTable,
  onTableSelect,
  onTablesLoaded,
}) => {
  const [tables, setTables] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Table preview state
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [previewData, setPreviewData] = useState<TablePreviewData | null>(null);
  const [previewTableName, setPreviewTableName] = useState<string>('');
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  useEffect(() => {
    if (schemaName) {
      loadTables();
    }
  }, [connectionId, schemaName]);

  const loadTables = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const tableList = await schemaAPI.getTables(connectionId, schemaName);
      setTables(tableList);
      // Notify parent component of loaded tables
      if (onTablesLoaded) {
        onTablesLoaded(tableList);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tables');
      console.error('Error loading tables:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreviewTable = async (tableName: string) => {
    setPreviewTableName(tableName);
    setIsLoadingPreview(true);
    setPreviewError(null);
    setPreviewData(null);
    onOpen();

    try {
      const result = await schemaAPI.previewTableData(connectionId, schemaName, tableName, 10);
      setPreviewData(result);
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : 'Failed to preview table data');
      console.error('Error previewing table:', err);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardBody className="flex items-center justify-center py-8">
          <Spinner size="sm" />
          <span className="text-sm text-gray-500 ml-2">Loading tables...</span>
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
            endContent={
              <Button
                isIconOnly
                size="sm"
                variant="light"
                onClick={loadTables}
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            }
          />
        </CardBody>
      </Card>
    );
  }

  if (tables.length === 0) {
    return (
      <Card>
        <CardBody className="text-center py-8">
          <TableIcon className="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p className="text-sm text-gray-500">No tables found in this schema</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody className="gap-0">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-sm">Tables ({tables.length})</h3>
          <Button
            isIconOnly
            size="sm"
            variant="light"
            onClick={loadTables}
            isLoading={isLoading}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-1 max-h-96 overflow-y-auto">
          {tables.map(table => (
            <div
              key={table}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                selectedTable === table
                  ? 'bg-blue-100 text-blue-900 font-medium'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <button
                onClick={() => onTableSelect(table)}
                className="flex-1 flex items-center gap-2 text-left"
              >
                <TableIcon className="h-4 w-4" />
                <span className="text-sm">{table}</span>
              </button>
              <Button
                isIconOnly
                size="sm"
                variant="light"
                onClick={(e) => {
                  e.stopPropagation();
                  handlePreviewTable(table);
                }}
                title="Preview data (10 rows)"
              >
                <Eye className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      </CardBody>

      {/* Table Preview Modal - Enhanced UI */}
      <Modal 
        isOpen={isOpen} 
        onClose={onClose}
        size="5xl"
        scrollBehavior="inside"
        classNames={{
          base: "bg-white/95 backdrop-blur-xl",
          header: "border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50",
          body: "p-6",
          footer: "border-t border-gray-200 bg-gray-50"
        }}
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-2 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
                    <Eye className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Table Preview: {previewTableName}
                    </h2>
                    <p className="text-sm text-gray-500 font-normal mt-0.5">
                      Showing first 10 rows from <span className="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">{schemaName}.{previewTableName}</span>
                    </p>
                  </div>
                </div>
              </ModalHeader>
              <ModalBody className="px-6 py-4">
                {isLoadingPreview ? (
                  <div className="flex flex-col items-center justify-center py-16 gap-4">
                    <Spinner size="lg" color="primary" />
                    <div className="text-center">
                      <p className="text-gray-700 font-medium text-lg">Loading table data...</p>
                      <p className="text-sm text-gray-400 mt-1">Querying database</p>
                    </div>
                  </div>
                ) : previewError ? (
                  <div className="py-8">
                    <Alert
                      color="danger"
                      variant="flat"
                      startContent={<AlertCircle className="h-5 w-5" />}
                      title="Error loading data"
                      description={previewError}
                      className="bg-red-50 border border-red-200"
                    />
                  </div>
                ) : previewData && previewData.columns.length > 0 ? (
                  <div className="space-y-4">
                    {/* Data Stats Bar */}
                    <div className="flex items-center gap-4 px-4 py-3 bg-gradient-to-r from-blue-50 via-purple-50 to-blue-50 rounded-xl border border-blue-100 shadow-sm">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 rounded-lg bg-blue-500 text-white">
                          <TableIcon className="h-3.5 w-3.5" />
                        </div>
                        <span className="text-sm font-semibold text-gray-700">
                          {previewData.columns.length} columns
                        </span>
                      </div>
                      <div className="h-5 w-px bg-gradient-to-b from-transparent via-gray-300 to-transparent" />
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 rounded-lg bg-purple-500 text-white">
                          <Database className="h-3.5 w-3.5" />
                        </div>
                        <span className="text-sm font-semibold text-gray-700">
                          {previewData.rows.length} rows
                        </span>
                      </div>
                    </div>

                    {/* Data Table */}
                    <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-md">
                      <Table 
                        aria-label="Table preview"
                        className="min-w-full"
                        isStriped
                        removeWrapper
                        classNames={{
                          base: "max-h-[500px]",
                          table: "min-w-full",
                          thead: "bg-gradient-to-r from-gray-100 via-blue-50 to-gray-100",
                          th: "bg-transparent text-gray-700 font-bold text-xs uppercase tracking-wider border-b-2 border-gray-300",
                          td: "text-sm text-gray-900 border-b border-gray-100",
                        }}
                      >
                        <TableHeader>
                          {previewData.columns.map((col, idx) => (
                            <TableColumn key={idx}>
                              <div className="flex items-center gap-2 py-1">
                                <span>{col}</span>
                              </div>
                            </TableColumn>
                          ))}
                        </TableHeader>
                        <TableBody>
                          {previewData.rows.length > 0 ? (
                            previewData.rows.map((row, rowIdx) => (
                              <TableRow 
                                key={rowIdx} 
                                className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-all duration-200"
                              >
                                {row.map((cell, cellIdx) => (
                                  <TableCell key={cellIdx}>
                                    {cell !== null && cell !== undefined ? (
                                      <span className="font-mono text-xs text-gray-800">{String(cell)}</span>
                                    ) : (
                                      <span className="text-gray-400 italic text-xs font-medium">null</span>
                                    )}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))
                          ) : (
                            <TableRow>
                              <TableCell colSpan={previewData.columns.length}>
                                <div className="text-center py-16">
                                  <div className="inline-block p-4 rounded-full bg-gray-100 mb-3">
                                    <TableIcon className="h-10 w-10 text-gray-400" />
                                  </div>
                                  <p className="text-gray-600 font-medium text-lg">No data found</p>
                                  <p className="text-sm text-gray-400 mt-1">This table appears to be empty</p>
                                </div>
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-20">
                    <div className="inline-block p-5 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-4">
                      <TableIcon className="h-14 w-14 text-gray-400" />
                    </div>
                    <p className="text-gray-600 font-semibold text-xl">No data to display</p>
                    <p className="text-sm text-gray-400 mt-2">This table may be empty or unavailable</p>
                  </div>
                )}
              </ModalBody>
              <ModalFooter className="px-6 py-4">
                <Button 
                  color="primary" 
                  variant="shadow"
                  onPress={onClose}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold px-6"
                >
                  Close
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </Card>
  );
};

export default TableList;

