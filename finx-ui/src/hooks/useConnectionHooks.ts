import { useConnection } from '@/contexts/ConnectionContext';
import type { AthenaConnectionConfig } from '@/lib/athenaClient';

/**
 * Custom hooks for working with cached connections
 */

/**
 * Get the current active connection config
 * Returns null if no connection is active
 */
export const useCurrentConnectionConfig = () => {
  const { currentConnection } = useConnection();
  return currentConnection?.config as AthenaConnectionConfig | null;
};

/**
 * Get a specific connection config by ID
 */
export const useConnectionConfig = (connectionId: string | undefined) => {
  const { getConnection } = useConnection();
  
  if (!connectionId) return null;
  
  const connection = getConnection(connectionId);
  return connection?.config as AthenaConnectionConfig | null;
};

/**
 * Check if there are any saved connections
 */
export const useHasSavedConnections = () => {
  const { connections } = useConnection();
  return connections.length > 0;
};

/**
 * Get the default connection (if any)
 */
export const useDefaultConnection = () => {
  const { connections } = useConnection();
  return connections.find(c => c.isDefault) || null;
};

/**
 * Get connections by type
 */
export const useConnectionsByType = (type: 'athena' | 'postgres' | 'mysql' | 'redshift') => {
  const { connections } = useConnection();
  return connections.filter(c => c.type === type);
};

/**
 * Quick access to Athena client with current connection
 */
export const useAthenaClient = () => {
  const config = useCurrentConnectionConfig();
  
  if (!config) {
    return {
      config: null,
      isReady: false,
      error: 'No active connection'
    };
  }

  return {
    config,
    isReady: true,
    error: null
  };
};

/**
 * Get connection metadata helper
 */
export const useConnectionMetadata = (connectionId?: string) => {
  const { currentConnection, getConnection } = useConnection();
  
  const connection = connectionId 
    ? getConnection(connectionId) 
    : currentConnection;

  return {
    catalog: connection?.metadata?.catalog,
    schema: connection?.metadata?.schema,
    region: connection?.metadata?.region,
    name: connection?.name,
    type: connection?.type,
    lastUsed: connection?.lastUsed
  };
};

export default {
  useCurrentConnectionConfig,
  useConnectionConfig,
  useHasSavedConnections,
  useDefaultConnection,
  useConnectionsByType,
  useAthenaClient,
  useConnectionMetadata
};
