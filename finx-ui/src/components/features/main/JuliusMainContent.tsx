import React, { useState } from 'react';
import { Search, Plus, Settings, Upload, MessageSquare, Sparkles } from 'lucide-react';
import { JuliusTemplateCards } from '.';
import '@/styles/components/julius-ai-styles.css';

interface JuliusMainContentProps {
  activeSection?: string;
}

export const JuliusMainContent: React.FC<JuliusMainContentProps> = ({
  activeSection = 'notebooks'
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const renderContent = () => {
    switch (activeSection) {
      case 'notebooks':
        return (
          <div className="max-w-7xl mx-auto">
            {/* Section Title */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Make a notebook for repeatable analysis
              </h2>
              <div className="julius-search-container max-w-md">
                <Search className="julius-search-icon" />
                <input
                  type="text"
                  placeholder="Search notebooks..."
                  className="julius-search-input"
                />
              </div>
            </div>

            {/* Template Cards Grid */}
            <JuliusTemplateCards searchTerm={searchTerm} />
          </div>
        );

      case 'chat':
        return (
          <div className="max-w-7xl mx-auto">
            <div className="text-center py-12">
              <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Chat Threads</h2>
              <p className="text-gray-600 mb-6">Start a new conversation or continue existing threads</p>
              <button className="julius-btn julius-btn-primary">
                <Plus className="h-4 w-4 mr-2" />
                New Chat
              </button>
            </div>
          </div>
        );

      case 'files':
        return (
          <div className="max-w-7xl mx-auto">
            <div className="text-center py-12">
              <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Files</h2>
              <p className="text-gray-600 mb-6">Upload and manage your data files</p>
              <button className="julius-btn julius-btn-primary">
                <Upload className="h-4 w-4 mr-2" />
                Upload File
              </button>
            </div>
          </div>
        );

      case 'data':
        return (
          <div className="max-w-7xl mx-auto">
            <div className="text-center py-12">
              <Settings className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Data Connectors</h2>
              <p className="text-gray-600 mb-6">Connect to external data sources</p>
              <button className="julius-btn julius-btn-primary">
                <Plus className="h-4 w-4 mr-2" />
                Add Connector
              </button>
            </div>
          </div>
        );

      default:
        return (
          <div className="max-w-7xl mx-auto">
            <JuliusTemplateCards searchTerm={searchTerm} />
          </div>
        );
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="julius-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              What do you want to analyze today?
            </h1>
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-blue-600 cursor-pointer hover:underline">
              Unlock all of Julius
            </div>
            <div className="text-sm text-blue-600 cursor-pointer hover:underline">
              OR
            </div>
            <button className="julius-btn julius-btn-secondary">
              <Upload className="h-4 w-4 mr-2" />
              Upload a file
            </button>
            <button className="julius-btn julius-btn-secondary">
              <MessageSquare className="h-4 w-4 mr-2" />
              Human examples
            </button>
            <button className="julius-btn julius-btn-primary">
              <Sparkles className="h-4 w-4 mr-2" />
              Calibrate Julius
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mt-6">
          <div className="julius-search-container">
            <Search className="julius-search-icon" />
            <input
              type="text"
              placeholder="Connect data and start chatting"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="julius-search-input"
            />
            <button className="absolute right-3 top-1/2 transform -translate-y-1/2 julius-btn julius-btn-primary px-3 py-1">
              <MessageSquare className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="mt-4 flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <span className="julius-badge julius-badge-blue">Default</span>
            <div className="julius-dropdown">
              <button className="julius-btn julius-btn-secondary text-sm">
                <Settings className="h-3 w-3 mr-1" />
                Tools
              </button>
            </div>
          </div>
          <div className="text-sm text-gray-600">Advanced Reasoning</div>
          <div className="text-sm text-gray-600">Extended Memory</div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto p-6">
        {renderContent()}
      </div>
    </div>
  );
};

export default JuliusMainContent;
