import React, { useState, useEffect } from 'react';
import { Card, CardBody, Tabs, Tab, Spinner, Alert, Button, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure, Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/react';
import { Database, Table as TableIcon, AlertCircle, RefreshCw, Network, Eye, Clock } from 'lucide-react';
import { createAthenaClient, type AthenaConnectionConfig, type AthenaDatabase, type AthenaTable, type AthenaQueryResult } from '@/lib/athenaClient';
// import { AthenaDiagramView } from '../../connections/AthenaDiagramView';

export interface AthenaSchemaExplorerProps {
  connectionConfig: AthenaConnectionConfig;
  connectionName?: string;
  catalogName?: string;
}

export const AthenaSchemaExplorer: React.FC<AthenaSchemaExplorerProps> = ({
  connectionConfig,
  connectionName = 'Athena Connection',
  catalogName = 'AwsDataCatalog',
}) => {
  const [databases, setDatabases] = useState<AthenaDatabase[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<string>('');
  const [tables, setTables] = useState<AthenaTable[]>([]);
  const [selectedTable, setSelectedTable] = useState<AthenaTable | null>(null);
  const [isLoadingDatabases, setIsLoadingDatabases] = useState(false);
  const [isLoadingTables, setIsLoadingTables] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'diagram'>('list');
  
  // Table preview state
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [previewData, setPreviewData] = useState<AthenaQueryResult | null>(null);
  const [previewTableName, setPreviewTableName] = useState<string>('');
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  useEffect(() => {
    loadDatabases();
  }, []);

  useEffect(() => {
    if (selectedDatabase) {
      loadTables(selectedDatabase);
    }
  }, [selectedDatabase]);

  const loadDatabases = async () => {
    setIsLoadingDatabases(true);
    setError(null);
    try {
      const client = createAthenaClient(connectionConfig);
      const dbList = await client.listDatabases(catalogName);
      setDatabases(dbList);
      
      // Auto-select first database or the one from config
      if (dbList.length > 0) {
        const defaultDb = connectionConfig.database || dbList[0].name;
        setSelectedDatabase(defaultDb);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load databases');
    } finally {
      setIsLoadingDatabases(false);
    }
  };

  const loadTables = async (databaseName: string) => {
    setIsLoadingTables(true);
    setError(null);
    setSelectedTable(null);
    try {
      const client = createAthenaClient(connectionConfig);
      const tableList = await client.listTables(databaseName, catalogName);
      setTables(tableList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tables');
    } finally {
      setIsLoadingTables(false);
    }
  };

  const handleTableSelect = (table: AthenaTable) => {
    setSelectedTable(table);
  };

  const handleRefresh = () => {
    if (selectedDatabase) {
      loadTables(selectedDatabase);
    } else {
      loadDatabases();
    }
  };

  const handlePreviewTable = async (tableName: string) => {
    setPreviewTableName(tableName);
    setIsLoadingPreview(true);
    setPreviewError(null);
    setPreviewData(null);
    onOpen();

    try {
      const client = createAthenaClient(connectionConfig);
      const result = await client.previewTable(tableName, selectedDatabase, 10);
      setPreviewData(result);
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : 'Failed to preview table data');
      console.error('Error previewing table:', err);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  return (
    <div className="w-full space-y-4">
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2">Athena Schema Explorer</h2>
              <p className="text-sm text-gray-600">
                Connection: <span className="font-semibold">{connectionName}</span>
                {catalogName && <span> | Catalog: <span className="font-semibold">{catalogName}</span></span>}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={viewMode === 'list' ? 'solid' : 'flat'}
                color={viewMode === 'list' ? 'primary' : 'default'}
                startContent={<TableIcon className="h-4 w-4" />}
                onClick={() => setViewMode('list')}
              >
                List View
              </Button>
              <Button
                size="sm"
                variant={viewMode === 'diagram' ? 'solid' : 'flat'}
                color={viewMode === 'diagram' ? 'primary' : 'default'}
                startContent={<Network className="h-4 w-4" />}
                onClick={() => setViewMode('diagram')}
              >
                Diagram View
              </Button>
              <Button
                size="sm"
                variant="flat"
                startContent={<RefreshCw className="h-4 w-4" />}
                onClick={handleRefresh}
                isLoading={isLoadingDatabases || isLoadingTables}
              >
                Refresh
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>

      {error && (
        <Alert
          color="danger"
          startContent={<AlertCircle className="h-4 w-4" />}
          title="Error"
          description={error}
        />
      )}

      {viewMode === 'diagram' && selectedDatabase && tables.length > 0 ? (
        <Card>
          <CardBody className="text-center py-12">
            <p className="text-gray-500">Diagram view coming soon</p>
            <p className="text-sm text-gray-400 mt-2">Diagram visualization feature will be added</p>
          </CardBody>
        </Card>
      ) : viewMode === 'diagram' && selectedDatabase ? (
        <Card>
          <CardBody className="text-center py-12">
            <p className="text-gray-500">No tables to display in diagram view</p>
            <p className="text-sm text-gray-400 mt-2">Select a database with tables to see the diagram</p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Column: Databases */}
          <div className="lg:col-span-1">
            <Card>
              <CardBody className="gap-4">
                <div className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">Databases</h3>
                </div>

                {isLoadingDatabases ? (
                  <div className="flex items-center justify-center py-8">
                    <Spinner size="sm" />
                  </div>
                ) : (
                  <div className="space-y-2">
                    {databases.map(db => (
                      <Button
                        key={db.name}
                        variant={selectedDatabase === db.name ? 'solid' : 'flat'}
                        color={selectedDatabase === db.name ? 'primary' : 'default'}
                        className="w-full justify-start"
                        onClick={() => setSelectedDatabase(db.name)}
                      >
                        {db.name}
                      </Button>
                    ))}
                    {databases.length === 0 && (
                      <p className="text-sm text-gray-500 text-center py-4">No databases found</p>
                    )}
                  </div>
                )}
              </CardBody>
            </Card>
          </div>

          {/* Middle Column: Tables */}
          <div className="lg:col-span-1">
            {selectedDatabase && (
              <Card>
                <CardBody className="gap-4">
                  <div className="flex items-center gap-2">
                    <TableIcon className="h-5 w-5 text-primary" />
                    <h3 className="font-semibold">Tables</h3>
                  </div>

                  {isLoadingTables ? (
                    <div className="flex items-center justify-center py-8">
                      <Spinner size="sm" />
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {tables.map(table => (
                        <div
                          key={table.name}
                          className={`flex items-center gap-2 p-2 rounded-lg transition-colors ${
                            selectedTable?.name === table.name
                              ? 'bg-primary text-primary-foreground'
                              : 'hover:bg-default-100'
                          }`}
                        >
                          <button
                            className="flex-1 flex flex-col items-start text-left"
                            onClick={() => handleTableSelect(table)}
                          >
                            <span className="font-medium">{table.name}</span>
                            {table.tableType && (
                              <span className="text-xs opacity-70">{table.tableType}</span>
                            )}
                          </button>
                          <Button
                            isIconOnly
                            size="sm"
                            variant="light"
                            onClick={(e) => {
                              e.stopPropagation();
                              handlePreviewTable(table.name);
                            }}
                            title="Preview data (10 rows)"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      {tables.length === 0 && (
                        <p className="text-sm text-gray-500 text-center py-4">No tables found</p>
                      )}
                    </div>
                  )}
                </CardBody>
              </Card>
            )}
          </div>

          {/* Right Column: Table Details */}
          <div className="lg:col-span-1">
            {selectedTable && (
              <Card>
                <CardBody className="gap-4">
                  <h3 className="font-semibold">Table: {selectedTable.name}</h3>
                  
                  <div>
                    <h4 className="text-sm font-semibold mb-2">Columns ({selectedTable.columns?.length || 0})</h4>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {selectedTable.columns?.map((col, idx) => (
                        <div key={idx} className="p-2 bg-gray-50 rounded">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {col.isPrimaryKey && (
                                <span className="text-yellow-600 text-xs" title="Primary Key">🔑</span>
                              )}
                              {col.isForeignKey && (
                                <span className="text-blue-600 text-xs" title="Foreign Key">🔗</span>
                              )}
                              <span className="font-medium text-sm">{col.name}</span>
                            </div>
                            <span className="text-xs text-gray-600 bg-gray-200 px-2 py-1 rounded">
                              {col.type}
                            </span>
                          </div>
                          {col.comment && (
                            <p className="text-xs text-gray-500 mt-1">{col.comment}</p>
                          )}
                          {col.referencedTable && (
                            <p className="text-xs text-blue-600 mt-1">
                              → {col.referencedTable}.{col.referencedColumn}
                            </p>
                          )}
                        </div>
                      ))}
                      {(!selectedTable.columns || selectedTable.columns.length === 0) && (
                        <p className="text-sm text-gray-500 text-center py-4">No columns information</p>
                      )}
                    </div>
                  </div>
                </CardBody>
              </Card>
            )}
          </div>
        </div>
      )}

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
                      Showing first 10 rows from <span className="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">{selectedDatabase}.{previewTableName}</span>
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
                      <p className="text-sm text-gray-400 mt-1">Executing query on AWS Athena</p>
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
                      {previewData.executionTime && (
                        <>
                          <div className="h-5 w-px bg-gradient-to-b from-transparent via-gray-300 to-transparent" />
                          <div className="flex items-center gap-2">
                            <div className="p-1.5 rounded-lg bg-green-500 text-white">
                              <Clock className="h-3.5 w-3.5" />
                            </div>
                            <span className="text-sm font-semibold text-gray-700">
                              {previewData.executionTime}ms
                            </span>
                          </div>
                        </>
                      )}
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
                                    {cell ? (
                                      <span className="font-mono text-xs text-gray-800">{cell}</span>
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
    </div>
  );
};

export default AthenaSchemaExplorer;
