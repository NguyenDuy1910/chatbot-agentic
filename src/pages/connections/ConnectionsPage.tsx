import React from 'react';
import { ConnectionDashboard } from '@/components/features/connections';

/**
 * Connections page component - content only
 * Handles database connections and management
 */
export const ConnectionsPage: React.FC = () => {
  return (
    <div className="h-full">
      <ConnectionDashboard />
    </div>
  );
};

export default ConnectionsPage;
