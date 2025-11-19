import React, { useState } from 'react';
import { Button } from '@heroui/react';
import { ArrowLeft } from 'lucide-react';
import { ConnectionDashboard, ConnectionWorkflow } from '@/components/features/data-connections';

/**
 * Connections page component - content only
 * Handles database connections and management
 */
export const ConnectionsPage: React.FC = () => {
  const [showWorkflow, setShowWorkflow] = useState(false);

  if (showWorkflow) {
    return (
      <div className="h-full">
        <ConnectionWorkflow onBack={() => setShowWorkflow(false)} forceNew={true} />
      </div>
    );
  }

  return (
    <div className="h-full">
      <ConnectionDashboard onNewConnection={() => setShowWorkflow(true)} />
    </div>
  );
};

export default ConnectionsPage;
