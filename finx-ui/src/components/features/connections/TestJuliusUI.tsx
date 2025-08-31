import React, { useState } from 'react';
import { Search, Plus, Settings, Activity, Grid } from 'lucide-react';
import '@/styles/components/julius-ai-styles.css';

// Simple test component for Julius AI UI
export const TestJuliusUI: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'connections' | 'templates' | 'stats'>('connections');

  return (
    <div className="h-screen flex julius-main-content">
      {/* Sidebar - Julius AI Style */}
      <div className="julius-sidebar">
        {/* Sidebar Header */}
        <div className="julius-sidebar-header">
          <div className="flex items-center space-x-3">
            <div className="julius-logo">
              <Settings className="h-4 w-4" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 text-sm">Data Connectors & MCPs</h2>
            </div>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            You can connect Julius to your data stores and business tools here.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex-1 p-4">
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab('connections')}
              className={`julius-nav-item ${activeTab === 'connections' ? 'active' : ''}`}
            >
              <Settings className="h-4 w-4" />
              My Connections
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`julius-nav-item ${activeTab === 'templates' ? 'active' : ''}`}
            >
              <Grid className="h-4 w-4" />
              Add connectors
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`julius-nav-item ${activeTab === 'stats' ? 'active' : ''}`}
            >
              <Activity className="h-4 w-4" />
              Statistics
            </button>
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-2">
            <div className="font-medium">Resources</div>
            <div className="space-y-1">
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">📚 Documentation</a>
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">💬 Community Slack</a>
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">🧪 Models Lab</a>
              <a href="#" className="block text-gray-600 hover:text-gray-900 text-xs">⬆️ Upgrade Subscription</a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <div className="julius-header">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {activeTab === 'connections' && 'My Connections'}
                {activeTab === 'templates' && 'Add connectors'}
                {activeTab === 'stats' && 'Statistics'}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {activeTab === 'connections' && 'Manage your active connections'}
                {activeTab === 'templates' && 'Choose from available connectors'}
                {activeTab === 'stats' && 'View connection analytics and performance'}
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button className="julius-btn julius-btn-secondary">
                Refresh
              </button>
              {activeTab === 'connections' && (
                <button className="julius-btn julius-btn-primary">
                  <Plus className="h-4 w-4 mr-2" />
                  New
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden julius-content">
          {activeTab === 'connections' && (
            <div className="p-6">
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">My Connections</h2>
                
                {/* Empty State */}
                <div className="julius-empty-state">
                  <Settings className="julius-empty-icon" />
                  <h3 className="julius-empty-title">No connections yet</h3>
                  <p className="julius-empty-description">
                    Get started by adding your first connection
                  </p>
                  <button className="julius-btn julius-btn-primary">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Connection
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="p-6 julius-content">
              <div className="mb-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-6">Add connectors</h2>
                
                {/* Search */}
                <div className="mb-6">
                  <div className="julius-search-container">
                    <Search className="julius-search-icon" />
                    <input
                      type="text"
                      placeholder="Search connectors..."
                      className="julius-search-input"
                    />
                  </div>
                </div>
                
                {/* Template Cards Grid */}
                <div className="julius-grid">
                  <div className="julius-template-card">
                    <div className="julius-template-icon">🗂️</div>
                    <div className="mb-4">
                      <h3 className="julius-template-title">Google Drive</h3>
                      <p className="julius-template-description">
                        Analyze your Google Drive files and folders
                      </p>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="julius-badge julius-badge-gray">Integration</span>
                        <span className="julius-badge julius-badge-blue">MCP</span>
                      </div>
                      <button className="julius-btn julius-btn-primary">
                        <Plus className="h-3 w-3 mr-1" />
                        Add
                      </button>
                    </div>
                  </div>

                  <div className="julius-template-card">
                    <div className="julius-template-icon">💳</div>
                    <div className="mb-4">
                      <h3 className="julius-template-title">Stripe</h3>
                      <p className="julius-template-description">
                        Track revenue, subscriptions, and refunds with clean Stripe analytics
                      </p>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="julius-badge julius-badge-gray">MCP</span>
                        <span className="julius-badge julius-badge-blue">MCP</span>
                      </div>
                      <button className="julius-btn julius-btn-primary">
                        <Plus className="h-3 w-3 mr-1" />
                        Add
                      </button>
                    </div>
                  </div>

                  <div className="julius-template-card">
                    <div className="julius-template-icon">📝</div>
                    <div className="mb-4">
                      <h3 className="julius-template-title">Notion</h3>
                      <p className="julius-template-description">
                        Read, update, and organize Notion pages programmatically within Julius
                      </p>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="julius-badge julius-badge-gray">MCP</span>
                        <span className="julius-badge julius-badge-blue">MCP</span>
                      </div>
                      <button className="julius-btn julius-btn-primary">
                        <Plus className="h-3 w-3 mr-1" />
                        Add
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h2>
              <p className="text-gray-600">Connection statistics will be displayed here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestJuliusUI;
