import React, { useState } from 'react';

interface SQLResult {
  sql: string;
  explanation: string;
}

interface ExecutionResult {
  results: {
    columns: string[];
    rows: any[];
    rowCount: number;
  };
  executionTime: number;
}

export interface Text2SQLInterfaceProps {
  onGenerateSQL?: (request: string) => Promise<SQLResult>;
  onExecuteSQL?: (sql: string) => Promise<ExecutionResult>;
  connections: Array<{ id: string; name: string; isConnected: boolean }>;
  activeConnectionId: string | null;
  onConnectionChange: (id: string) => void;
}

export const Text2SQLInterface: React.FC<Text2SQLInterfaceProps> = ({
  onGenerateSQL,
  onExecuteSQL,
  connections,
  activeConnectionId,
  onConnectionChange
}) => {
  const [query, setQuery] = useState('');
  const [generatedSQL, setGeneratedSQL] = useState('');
  const [results, setResults] = useState<ExecutionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerate = async () => {
    if (!query.trim() || !activeConnectionId) return;
    
    setIsLoading(true);
    try {
      const result = await onGenerateSQL?.(query);
      if (result) {
        setGeneratedSQL(result.sql);
      }
    } catch (error) {
      console.error('Error generating SQL:', error);
    }
    setIsLoading(false);
  };

  const handleExecute = async () => {
    if (!generatedSQL.trim() || !activeConnectionId) return;
    
    setIsLoading(true);
    try {
      const result = await onExecuteSQL?.(generatedSQL);
      if (result) {
        setResults(result);
      }
    } catch (error) {
      console.error('Error executing SQL:', error);
    }
    setIsLoading(false);
  };

  return (
    <div className="w-full p-4 space-y-4">
      <div className="flex gap-2 items-center">
        <select 
          value={activeConnectionId || ''} 
          onChange={(e) => onConnectionChange(e.target.value)}
          className="border rounded px-2 py-1"
        >
          <option value="">Select Connection</option>
          {connections.map(conn => (
            <option 
              key={conn.id} 
              value={conn.id}
              disabled={!conn.isConnected}
            >
              {conn.name} {!conn.isConnected && '(Disconnected)'}
            </option>
          ))}
        </select>
      </div>

      <div>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe your query in natural language..."
          className="w-full p-2 border rounded"
          rows={4}
        />
        <button 
          onClick={handleGenerate}
          disabled={!query.trim() || !activeConnectionId || isLoading}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          Generate SQL
        </button>
      </div>

      {generatedSQL && (
        <div>
          <h3>Generated SQL:</h3>
          <pre className="bg-gray-100 p-4 rounded">
            {generatedSQL}
          </pre>
          <button
            onClick={handleExecute}
            disabled={!generatedSQL.trim() || !activeConnectionId || isLoading}
            className="mt-2 px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50"
          >
            Execute Query
          </button>
        </div>
      )}

      {results && (
        <div>
          <h3>Results:</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full border">
              <thead>
                <tr>
                  {results.results.columns.map((col, i) => (
                    <th key={i} className="border p-2">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.results.rows.map((row, i) => (
                  <tr key={i}>
                    {results.results.columns.map((col, j) => (
                      <td key={j} className="border p-2">{row[col]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Execution time: {results.executionTime}ms
          </p>
        </div>
      )}
    </div>
  );
};
