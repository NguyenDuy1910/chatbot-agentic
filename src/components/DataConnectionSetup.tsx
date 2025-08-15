import React from 'react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';

interface Connector {
  name: string;
  description: string;
  icon: string;
  type: 'integration' | 'database' | 'mcp';
  isNew?: boolean;
}

const connectors: Connector[] = [
  {
    name: 'Google Drive',
    description: 'Access your Google Drive files and folders',
    icon: '/icons/google-drive.svg',
    type: 'integration'
  },
  {
    name: 'Microsoft OneDrive',
    description: 'Access and manage OneDrive files and folders',
    icon: '/icons/onedrive.svg',
    type: 'integration',
    isNew: true
  },
  {
    name: 'SharePoint',
    description: 'Access your SharePoint documents and files for business files',
    icon: '/icons/sharepoint.svg',
    type: 'integration',
    isNew: true
  },
  {
    name: 'Postgres',
    description: 'Database',
    icon: '/icons/postgres.svg',
    type: 'database'
  },
  {
    name: 'Supabase',
    description: 'Database',
    icon: '/icons/supabase.svg',
    type: 'database'
  },
  {
    name: 'MCP',
    description: 'Integration',
    icon: '/icons/mcp.svg',
    type: 'mcp'
  }
];

const DataConnectionSetup: React.FC = () => {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Add connectors</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {connectors.map((connector) => (
            <Card key={connector.name} className="p-4 hover:bg-gray-50 cursor-pointer relative">
              <div className="flex items-start space-x-4">
                <img src={connector.icon} alt={connector.name} className="w-10 h-10" />
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-medium">{connector.name}</h3>
                    {connector.isNew && (
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded">
                        New
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{connector.description}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <Card className="p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Whitelist IP Address for Database Connections</h2>
          <Button variant="outline" className="text-sm">
            Copy
          </Button>
        </div>
        <p className="text-sm text-gray-600 mb-2">
          If your database requires IP whitelisting, add this IP address to your allowed connections:
        </p>
        <div className="bg-gray-50 p-3 rounded-md font-mono text-sm">
          35.225.57.12, 35.202.28.218, 35.184.233.185
        </div>
        <p className="text-xs text-gray-500 mt-2">
          This IP address is automatically updated when our infrastructure changes.
        </p>
        <div className="flex items-center mt-4 space-x-2">
          {['google-cloud', 'azure', 'postgres', 'snowflake'].map((icon) => (
            <img
              key={icon}
              src={`/icons/${icon}.svg`}
              alt={icon}
              className="w-6 h-6"
            />
          ))}
        </div>
      </Card>

      <div className="flex justify-between items-center">
        <Button variant="outline">Need another connection?</Button>
        <Button>Request connector</Button>
      </div>
    </div>
  );
};

export default DataConnectionSetup;
