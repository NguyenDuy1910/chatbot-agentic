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
      <div className="h-full p-6">
        <div className="flex items-center gap-2 mb-4">
          <Button
            isIconOnly
            variant="light"
            onPress={() => setShowWorkflow(false)}
            startContent={<ArrowLeft className="h-4 w-4" />}
          />
          <h1 className="text-3xl font-bold">Create New Connection</h1>
        </div>
        <ConnectionWorkflow onBack={() => setShowWorkflow(false)} />
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
