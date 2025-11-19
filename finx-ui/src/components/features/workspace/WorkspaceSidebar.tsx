import React from 'react';
import {
  Plus, Settings, Grid, FileText, Users, BarChart,
  Database, MessageSquare, Sparkles, Upload, Zap
} from 'lucide-react';
import '@/styles/components/julius-ai-styles.css';

interface JuliusSidebarProps {
  activeSection?: string;
  onSectionChange?: (section: string) => void;
}

export const JuliusSidebar: React.FC<JuliusSidebarProps> = ({
  activeSection = 'notebooks',
  onSectionChange
}) => {
  const handleSectionClick = (section: string) => {
    if (onSectionChange) {
      onSectionChange(section);
    }
  };

  return (
    <div className="julius-sidebar">
      {/* Sidebar Header */}
      <div className="julius-sidebar-header">
        <div className="flex items-center space-x-3">
          <div className="julius-logo">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900 text-sm">Julius</h2>
          </div>
        </div>
        <div className="flex items-center space-x-2 mt-3">
          <div className="flex items-center space-x-1 text-xs text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Connected</span>
          </div>
          <div className="flex items-center space-x-1 text-xs text-blue-600">
            <Zap className="h-3 w-3" />
            <span>4</span>
          </div>
          <div className="flex items-center space-x-1 text-xs text-gray-600">
            <Settings className="h-3 w-3" />
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <div className="julius-nav-menu">
        <div className="px-3 py-2">
          <button className="julius-btn julius-btn-primary w-full">
            <Plus className="h-4 w-4 mr-2" />
            New
          </button>
        </div>

        <div className="px-3 py-2">
          <div className="text-xs font-medium text-gray-500 mb-2">Personal Workspace</div>
          <div className="space-y-1">
            <button
              onClick={() => handleSectionClick('chat')}
              className={`julius-nav-item ${activeSection === 'chat' ? 'active' : ''}`}
            >
              <FileText className="h-4 w-4 mr-3" />
              Chat Threads
              <span className="ml-auto text-xs text-gray-500">2</span>
              <div className="julius-nav-arrow">›</div>
            </button>
            <button
              onClick={() => handleSectionClick('notebooks')}
              className={`julius-nav-item ${activeSection === 'notebooks' ? 'active' : ''}`}
            >
              <Grid className="h-4 w-4 mr-3" />
              Notebooks
              <span className="ml-auto text-xs text-gray-500">4</span>
            </button>
            <button
              onClick={() => handleSectionClick('files')}
              className={`julius-nav-item ${activeSection === 'files' ? 'active' : ''}`}
            >
              <Upload className="h-4 w-4 mr-3" />
              Files
            </button>
            <button
              onClick={() => handleSectionClick('data')}
              className={`julius-nav-item ${activeSection === 'data' ? 'active' : ''}`}
            >
              <Database className="h-4 w-4 mr-3" />
              Data Connectors
              <span className="ml-auto text-xs text-gray-500">5</span>
            </button>
            <button className="julius-nav-item">
              <MessageSquare className="h-4 w-4 mr-3" />
              Inbox
            </button>
          </div>
        </div>

        <div className="px-3 py-2">
          <div className="text-xs font-medium text-gray-500 mb-2">Resources</div>
          <div className="space-y-1">
            <button className="julius-nav-item">
              <FileText className="h-4 w-4 mr-3" />
              Documentation
            </button>
            <button className="julius-nav-item">
              <Users className="h-4 w-4 mr-3" />
              Community Slack
            </button>
            <button className="julius-nav-item">
              <BarChart className="h-4 w-4 mr-3" />
              Models Lab
            </button>
            <button className="julius-nav-item">
              <Settings className="h-4 w-4 mr-3" />
              Upgrade Subscription
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="julius-sidebar-footer">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
            N
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-gray-900 truncate">Nguyễn Đình Quốc Duy</div>
            <div className="text-xs text-gray-500">Google • nguyendinhduy@gmail.com</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JuliusSidebar;
