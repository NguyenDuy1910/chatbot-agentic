import React, { useState } from 'react';
import { ButtonDemo } from '@/components/demo';
import { APIIntegrationDemo } from '@/components/demo/APIIntegrationDemo';
import { AuthDemo } from '@/components/demo/AuthDemo';

/**
 * Demo Page - Showcases UI components and API integration
 */
export const DemoPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'auth' | 'api' | 'ui'>('auth');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🧪 Demo & Testing
          </h1>
          <p className="text-gray-600">
            Test UI components và API integrations
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('auth')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'auth'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔐 Authentication
              </button>
              <button
                onClick={() => setActiveTab('api')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'api'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔌 API Integration
              </button>
              <button
                onClick={() => setActiveTab('ui')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'ui'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🎨 UI Components
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'auth' && <AuthDemo />}
            {activeTab === 'api' && <APIIntegrationDemo />}
            {activeTab === 'ui' && <ButtonDemo />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoPage;
