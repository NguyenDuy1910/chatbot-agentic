import React, { useState } from 'react';
import { Text2SQLRequest } from '@/types/database';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { 
  Play, 
  Copy, 
  RotateCcw, 
  Sparkles, 
  Database,
  Code,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Text2SQLInterfaceProps {
  connections: Array<{ id: string; name: string; isConnected: boolean }>;
  activeConnectionId: string | null;
  onConnectionChange: (connectionId: string) => void;
  onGenerateSQL: (request: Text2SQLRequest) => Promise<{ sql: string; explanation: string }>;
  onExecuteSQL: (sql: string) => Promise<any>;
  queryHistory?: Array<{ naturalLanguage: string; generatedSQL: string; executedAt: Date }>;
}

export const Text2SQLInterface: React.FC<Text2SQLInterfaceProps> = ({
  connections,
  activeConnectionId,
  onConnectionChange,
  onGenerateSQL,
  onExecuteSQL,
  queryHistory = []
}) => {
  const [naturalQuery, setNaturalQuery] = useState('');
  const [generatedSQL, setGeneratedSQL] = useState('');
  const [explanation, setExplanation] = useState('');
  const [queryResult, setQueryResult] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [includeSchema, setIncludeSchema] = useState(true);

  const handleGenerateSQL = async () => {
    if (!naturalQuery.trim() || !activeConnectionId) return;

    setIsGenerating(true);
    setError(null);
    setGeneratedSQL('');
    setExplanation('');

    try {
      const result = await onGenerateSQL({
        query: naturalQuery,
        connectionId: activeConnectionId,
        includeSchema,
      });
      
      setGeneratedSQL(result.sql);
      setExplanation(result.explanation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate SQL');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteSQL = async () => {
    if (!generatedSQL.trim()) return;

    setIsExecuting(true);
    setError(null);
    setQueryResult(null);

    try {
      const result = await onExecuteSQL(generatedSQL);
      setQueryResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute SQL');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleCopySQL = () => {
    navigator.clipboard.writeText(generatedSQL);
  };

  const handleReset = () => {
    setNaturalQuery('');
    setGeneratedSQL('');
    setExplanation('');
    setQueryResult(null);
    setError(null);
  };

  const handleHistorySelect = (historyItem: any) => {
    setNaturalQuery(historyItem.naturalLanguage);
    setGeneratedSQL(historyItem.generatedSQL);
  };

  const activeConnection = connections.find(c => c.id === activeConnectionId);

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            <h2 className="text-lg font-semibold">Text-to-SQL</h2>
            <Badge variant="outline" className="bg-blue-50 text-blue-700">
              Natural Language → SQL
            </Badge>
          </div>
          
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
        </div>

        {/* Connection Selector */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium">Database:</label>
          <Select
            value={activeConnectionId || ''}
            onChange={(e) => onConnectionChange(e.target.value)}
            className="w-auto min-w-48"
          >
            <option value="">Select a database</option>
            {connections.map(conn => (
              <option key={conn.id} value={conn.id} disabled={!conn.isConnected}>
                {conn.name} {!conn.isConnected ? '(Disconnected)' : ''}
              </option>
            ))}
          </Select>
          
          {activeConnection && (
            <Badge 
              variant={activeConnection.isConnected ? 'default' : 'destructive'}
              className="text-xs"
            >
              {activeConnection.isConnected ? 'Connected' : 'Disconnected'}
            </Badge>
          )}
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 overflow-hidden">
        {/* Input Section */}
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">
              Natural Language Query
            </label>
            <Textarea
              value={naturalQuery}
              onChange={(e) => setNaturalQuery(e.target.value)}
              placeholder="Ask in plain English: 'Show me all users who signed up last month' or 'What are the top 10 selling products?'"
              rows={6}
              className="resize-none"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="includeSchema"
              checked={includeSchema}
              onChange={(e) => setIncludeSchema(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="includeSchema" className="text-sm">
              Include database schema in context
            </label>
          </div>

          <Button
            onClick={handleGenerateSQL}
            disabled={!naturalQuery.trim() || !activeConnectionId || isGenerating}
            className="w-full"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            {isGenerating ? 'Generating...' : 'Generate SQL'}
          </Button>

          {/* Query History */}
          {queryHistory.length > 0 && (
            <div className="border rounded-lg p-3">
              <h3 className="text-sm font-medium mb-2">Recent Queries</h3>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {queryHistory.slice(0, 5).map((item, index) => (
                  <div
                    key={index}
                    className="text-xs p-2 bg-muted/50 rounded cursor-pointer hover:bg-muted"
                    onClick={() => handleHistorySelect(item)}
                  >
                    <div className="font-medium truncate">{item.naturalLanguage}</div>
                    <div className="text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {item.executedAt.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Generated SQL Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Generated SQL</label>
            {generatedSQL && (
              <div className="flex gap-1">
                <Button variant="ghost" size="sm" onClick={handleCopySQL}>
                  <Copy className="h-3 w-3 mr-1" />
                  Copy
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleExecuteSQL}
                  disabled={!generatedSQL.trim() || isExecuting || !activeConnection?.isConnected}
                >
                  <Play className="h-3 w-3 mr-1" />
                  {isExecuting ? 'Executing...' : 'Execute'}
                </Button>
              </div>
            )}
          </div>

          <div className="border rounded-lg h-48 flex flex-col">
            {generatedSQL ? (
              <div className="flex-1 p-3 font-mono text-sm bg-muted/20 overflow-auto">
                <pre className="whitespace-pre-wrap">{generatedSQL}</pre>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Code className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Generated SQL will appear here</p>
                </div>
              </div>
            )}
          </div>

          {explanation && (
            <div className="border rounded-lg p-3 bg-blue-50/50">
              <h4 className="text-sm font-medium mb-1">Explanation</h4>
              <p className="text-sm text-muted-foreground">{explanation}</p>
            </div>
          )}

          {error && (
            <div className="border rounded-lg p-3 bg-red-50 border-red-200">
              <div className="flex items-center gap-2 text-red-800">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm font-medium">Error</span>
              </div>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <label className="text-sm font-medium">Query Results</label>
          
          <div className="border rounded-lg h-96 flex flex-col">
            {queryResult ? (
              <div className="flex-1 overflow-hidden flex flex-col">
                <div className="border-b p-2 bg-muted/20 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>
                      {queryResult.results?.rowCount || 0} rows
                      {queryResult.executionTime && ` • ${queryResult.executionTime}ms`}
                    </span>
                  </div>
                </div>
                
                {queryResult.results?.rows.length > 0 ? (
                  <div className="flex-1 overflow-auto">
                    <table className="w-full text-xs">
                      <thead className="bg-muted/50 sticky top-0">
                        <tr>
                          {queryResult.results.columns.map((col: string) => (
                            <th key={col} className="text-left p-2 font-medium border-r">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResult.results.rows.map((row: any, index: number) => (
                          <tr key={index} className="border-b hover:bg-muted/20">
                            {queryResult.results.columns.map((col: string) => (
                              <td key={col} className="p-2 border-r">
                                {row[col]?.toString() || ''}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-muted-foreground">
                    <p className="text-sm">No data returned</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Database className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Query results will appear here</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
