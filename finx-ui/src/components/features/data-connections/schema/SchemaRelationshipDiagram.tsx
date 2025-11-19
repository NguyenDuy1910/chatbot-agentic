import React, { useState, useEffect } from 'react';
import { Card, CardBody, Button, Spinner, Chip } from '@heroui/react';
import { 
  Database, 
  Table as TableIcon, 
  Key, 
  Link2, 
  ArrowRight, 
  Maximize2, 
  Minimize2,
  ZoomIn,
  ZoomOut,
  Move
} from 'lucide-react';
import { schemaAPI } from '@/lib/schemaAPI';
import { TableInfo } from '@/types/features/connections';

export interface SchemaRelationshipDiagramProps {
  connectionId: string;
  schemaName: string;
  tables: string[];
}

interface TablePosition {
  x: number;
  y: number;
}

export const SchemaRelationshipDiagram: React.FC<SchemaRelationshipDiagramProps> = ({
  connectionId,
  schemaName,
  tables,
}) => {
  const [tablesData, setTablesData] = useState<Map<string, TableInfo>>(new Map());
  const [isLoading, setIsLoading] = useState(false);
  const [tablePositions, setTablePositions] = useState<Map<string, TablePosition>>(new Map());
  const [zoom, setZoom] = useState(1);
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);

  useEffect(() => {
    loadTablesData();
  }, [connectionId, schemaName, tables]);

  const loadTablesData = async () => {
    if (tables.length === 0) return;

    setIsLoading(true);
    const newTablesData = new Map<string, TableInfo>();
    const newPositions = new Map<string, TablePosition>();

    // Calculate positions in a grid layout
    const cols = Math.ceil(Math.sqrt(tables.length));
    const horizontalSpacing = 320;
    const verticalSpacing = 280;

    try {
      for (let i = 0; i < tables.length; i++) {
        const tableName = tables[i];
        try {
          const tableInfo = await schemaAPI.getTableDetails(
            connectionId,
            schemaName,
            tableName
          );
          newTablesData.set(tableName, tableInfo);

          // Position tables in grid
          const row = Math.floor(i / cols);
          const col = i % cols;
          newPositions.set(tableName, {
            x: col * horizontalSpacing + 50,
            y: row * verticalSpacing + 50,
          });
        } catch (err) {
          console.error(`Failed to load table ${tableName}:`, err);
        }
      }

      setTablesData(newTablesData);
      setTablePositions(newPositions);
    } finally {
      setIsLoading(false);
    }
  };

  const renderRelationshipLine = (
    from: TableInfo,
    to: string,
    fromPos: TablePosition,
    toPos: TablePosition
  ) => {
    const startX = fromPos.x + 140; // Center of card
    const startY = fromPos.y + 40;
    const endX = toPos.x + 140;
    const endY = toPos.y + 40;

    // Calculate control points for curved line
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2;

    return (
      <g key={`${from.name}-${to}`}>
        {/* Curved line */}
        <path
          d={`M ${startX} ${startY} Q ${midX} ${midY} ${endX} ${endY}`}
          stroke="#10b981"
          strokeWidth="2"
          fill="none"
          strokeDasharray="5,5"
          className="opacity-60 hover:opacity-100 transition-opacity"
        />
        {/* Arrow head */}
        <polygon
          points={`${endX},${endY} ${endX - 8},${endY - 5} ${endX - 8},${endY + 5}`}
          fill="#10b981"
          className="opacity-60"
        />
        {/* Label */}
        <text
          x={midX}
          y={midY - 10}
          fontSize="10"
          fill="#059669"
          className="font-semibold"
        >
          FK
        </text>
      </g>
    );
  };

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardBody className="flex flex-col items-center justify-center py-16">
          <Spinner size="lg" color="primary" />
          <p className="text-gray-600 font-medium mt-4">Loading schema relationships...</p>
          <p className="text-sm text-gray-400 mt-1">Analyzing {tables.length} tables</p>
        </CardBody>
      </Card>
    );
  }

  if (tablesData.size === 0) {
    return (
      <Card className="h-full">
        <CardBody className="flex flex-col items-center justify-center py-16 text-center">
          <div className="p-6 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-4">
            <Database className="h-16 w-16 text-gray-400" />
          </div>
          <p className="text-gray-600 font-medium text-lg">No Tables to Display</p>
          <p className="text-sm text-gray-400 mt-2">Add tables to see their relationships</p>
        </CardBody>
      </Card>
    );
  }

  const width = Math.max(1200, ...Array.from(tablePositions.values()).map(p => p.x + 300));
  const height = Math.max(800, ...Array.from(tablePositions.values()).map(p => p.y + 250));

  return (
    <Card className={`${isExpanded ? 'fixed inset-4 z-50' : 'h-full'}`}>
      <CardBody className="p-6 gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
              <Database className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Schema Relationships
              </h3>
              <p className="text-sm text-gray-500 mt-0.5">
                {tablesData.size} tables • {schemaName}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              isIconOnly
              size="sm"
              variant="flat"
              onPress={() => setZoom(Math.max(0.5, zoom - 0.1))}
              title="Zoom Out"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Chip size="sm" variant="flat">
              {Math.round(zoom * 100)}%
            </Chip>
            <Button
              isIconOnly
              size="sm"
              variant="flat"
              onPress={() => setZoom(Math.min(2, zoom + 0.1))}
              title="Zoom In"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              isIconOnly
              size="sm"
              variant="flat"
              onPress={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? "Exit Fullscreen" : "Fullscreen"}
            >
              {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {/* Diagram Canvas */}
        <div className="relative bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 rounded-xl border-2 border-blue-100 overflow-auto"
          style={{ height: isExpanded ? 'calc(100vh - 200px)' : '600px' }}
        >
          <svg
            width={width * zoom}
            height={height * zoom}
            className="absolute top-0 left-0"
            style={{ transform: `scale(${zoom})`, transformOrigin: '0 0' }}
          >
            {/* Render relationship lines */}
            {Array.from(tablesData.entries()).map(([tableName, tableInfo]) => {
              const fromPos = tablePositions.get(tableName);
              if (!fromPos) return null;

              return tableInfo.foreign_keys.map(fk => {
                const toPos = tablePositions.get(fk.referenced_table);
                if (!toPos || !tablesData.has(fk.referenced_table)) return null;
                return renderRelationshipLine(tableInfo, fk.referenced_table, fromPos, toPos);
              });
            })}
          </svg>

          {/* Render table cards */}
          <div className="relative" style={{ width: width, height: height }}>
            {Array.from(tablesData.entries()).map(([tableName, tableInfo]) => {
              const pos = tablePositions.get(tableName);
              if (!pos) return null;

              const isSelected = selectedTable === tableName;
              const hasRelationships = tableInfo.foreign_keys.length > 0 || 
                Array.from(tablesData.values()).some(t => 
                  t.foreign_keys.some(fk => fk.referenced_table === tableName)
                );

              return (
                <div
                  key={tableName}
                  className={`absolute bg-white rounded-lg shadow-xl border-2 transition-all cursor-pointer ${
                    isSelected 
                      ? 'border-blue-500 shadow-2xl ring-4 ring-blue-200' 
                      : hasRelationships
                      ? 'border-green-300 hover:border-green-500'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                  style={{
                    left: pos.x,
                    top: pos.y,
                    width: '280px',
                    transform: `scale(${zoom})`,
                    transformOrigin: '0 0',
                  }}
                  onClick={() => setSelectedTable(isSelected ? null : tableName)}
                >
                  {/* Table Header */}
                  <div className={`px-4 py-3 rounded-t-lg ${
                    isSelected 
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600' 
                      : 'bg-gradient-to-r from-gray-700 to-gray-800'
                  } text-white`}>
                    <div className="flex items-center gap-2">
                      <TableIcon className="h-4 w-4" />
                      <span className="font-bold text-sm truncate">{tableInfo.name}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      {tableInfo.primary_keys.length > 0 && (
                        <Chip size="sm" variant="flat" className="bg-white/20 text-white h-5">
                          <Key className="h-2.5 w-2.5 mr-1" />
                          {tableInfo.primary_keys.length} PK
                        </Chip>
                      )}
                      {tableInfo.foreign_keys.length > 0 && (
                        <Chip size="sm" variant="flat" className="bg-white/20 text-white h-5">
                          <Link2 className="h-2.5 w-2.5 mr-1" />
                          {tableInfo.foreign_keys.length} FK
                        </Chip>
                      )}
                    </div>
                  </div>

                  {/* Columns List */}
                  <div className="px-3 py-2 max-h-48 overflow-y-auto divide-y divide-gray-100">
                    {tableInfo.columns.slice(0, 8).map(col => (
                      <div key={col.name} className="py-2 flex items-center justify-between">
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          <div className={`p-1 rounded ${
                            col.isPrimaryKey 
                              ? 'bg-blue-100 text-blue-600' 
                              : col.isForeignKey 
                              ? 'bg-green-100 text-green-600' 
                              : 'bg-gray-100 text-gray-500'
                          }`}>
                            {col.isPrimaryKey ? (
                              <Key className="h-2.5 w-2.5" />
                            ) : col.isForeignKey ? (
                              <Link2 className="h-2.5 w-2.5" />
                            ) : null}
                          </div>
                          <span className="font-mono text-xs truncate">{col.name}</span>
                        </div>
                        <span className="text-[10px] text-gray-500 bg-gray-100 px-2 py-0.5 rounded ml-2">
                          {col.type.split('(')[0]}
                        </span>
                      </div>
                    ))}
                    {tableInfo.columns.length > 8 && (
                      <div className="py-2 text-center text-xs text-gray-400">
                        +{tableInfo.columns.length - 8} more columns
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-6 px-4 py-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-500" />
            <span className="text-xs font-medium text-gray-700">Primary Key</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500" />
            <span className="text-xs font-medium text-gray-700">Foreign Key</span>
          </div>
          <div className="flex items-center gap-2">
            <svg width="40" height="4">
              <line x1="0" y1="2" x2="40" y2="2" stroke="#10b981" strokeWidth="2" strokeDasharray="5,5" />
            </svg>
            <span className="text-xs font-medium text-gray-700">Relationship</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

export default SchemaRelationshipDiagram;
