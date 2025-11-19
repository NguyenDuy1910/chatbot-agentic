import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AthenaConnectionConfig } from '@/lib/athenaClient';

/**
 * Connection data stored in session
 */
export interface StoredConnection {
  id: string;
  name: string;
  type: 'athena' | 'postgres' | 'mysql' | 'redshift';
  config: AthenaConnectionConfig | any; // Can extend to other connection types
  lastUsed: Date;
  isDefault?: boolean;
  metadata?: {
    catalog?: string;
    schema?: string;
    region?: string;
  };
}

interface ConnectionContextType {
  connections: StoredConnection[];
  currentConnection: StoredConnection | null;
  addConnection: (connection: Omit<StoredConnection, 'id' | 'lastUsed'>) => void;
  removeConnection: (id: string) => void;
  setCurrentConnection: (id: string) => void;
  getConnection: (id: string) => StoredConnection | undefined;
  updateConnectionMetadata: (id: string, metadata: Partial<StoredConnection['metadata']>) => void;
  clearConnections: () => void;
}

const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined);

export const useConnection = () => {
  const context = useContext(ConnectionContext);
  if (context === undefined) {
    throw new Error('useConnection must be used within a ConnectionProvider');
  }
  return context;
};

interface ConnectionProviderProps {
  children: ReactNode;
}

const STORAGE_KEY = 'vikki_connections';

export const ConnectionProvider: React.FC<ConnectionProviderProps> = ({ children }) => {
  const [connections, setConnections] = useState<StoredConnection[]>([]);
  const [currentConnection, setCurrentConnectionState] = useState<StoredConnection | null>(null);

  // Load connections from sessionStorage on mount
  useEffect(() => {
    loadConnections();
  }, []);

  // Save connections to sessionStorage whenever they change
  useEffect(() => {
    if (connections.length > 0) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(connections));
    }
  }, [connections]);

  const loadConnections = () => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as StoredConnection[];
        // Convert date strings back to Date objects
        const withDates = parsed.map(conn => ({
          ...conn,
          lastUsed: new Date(conn.lastUsed)
        }));
        setConnections(withDates);
        
        // Set current connection to the last used or default
        const defaultConn = withDates.find(c => c.isDefault) || withDates[0];
        if (defaultConn) {
          setCurrentConnectionState(defaultConn);
        }
      }
    } catch (error) {
      console.error('Failed to load connections from session:', error);
    }
  };

  const addConnection = (connection: Omit<StoredConnection, 'id' | 'lastUsed'>) => {
    const newConnection: StoredConnection = {
      ...connection,
      id: `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      lastUsed: new Date()
    };

    setConnections(prev => {
      // If this is set as default, unset other defaults
      if (newConnection.isDefault) {
        return [...prev.map(c => ({ ...c, isDefault: false })), newConnection];
      }
      return [...prev, newConnection];
    });

    // Set as current connection
    setCurrentConnectionState(newConnection);

    console.log('✅ Connection added to session:', newConnection.name);
  };

  const removeConnection = (id: string) => {
    setConnections(prev => prev.filter(c => c.id !== id));
    
    if (currentConnection?.id === id) {
      setCurrentConnectionState(null);
    }

    console.log('🗑️ Connection removed from session:', id);
  };

  const setCurrentConnection = (id: string) => {
    const connection = connections.find(c => c.id === id);
    if (connection) {
      // Update last used time
      const updated = { ...connection, lastUsed: new Date() };
      setConnections(prev =>
        prev.map(c => c.id === id ? updated : c)
      );
      setCurrentConnectionState(updated);
      console.log('🔄 Current connection set to:', connection.name);
    }
  };

  const getConnection = (id: string): StoredConnection | undefined => {
    return connections.find(c => c.id === id);
  };

  const updateConnectionMetadata = (id: string, metadata: Partial<StoredConnection['metadata']>) => {
    setConnections(prev =>
      prev.map(c =>
        c.id === id
          ? { ...c, metadata: { ...c.metadata, ...metadata } }
          : c
      )
    );

    if (currentConnection?.id === id) {
      setCurrentConnectionState(prev =>
        prev ? { ...prev, metadata: { ...prev.metadata, ...metadata } } : null
      );
    }

    console.log('📝 Connection metadata updated:', id, metadata);
  };

  const clearConnections = () => {
    setConnections([]);
    setCurrentConnectionState(null);
    sessionStorage.removeItem(STORAGE_KEY);
    console.log('🧹 All connections cleared from session');
  };

  const value: ConnectionContextType = {
    connections,
    currentConnection,
    addConnection,
    removeConnection,
    setCurrentConnection,
    getConnection,
    updateConnectionMetadata,
    clearConnections
  };

  return (
    <ConnectionContext.Provider value={value}>
      {children}
    </ConnectionContext.Provider>
  );
};

export default ConnectionProvider;
