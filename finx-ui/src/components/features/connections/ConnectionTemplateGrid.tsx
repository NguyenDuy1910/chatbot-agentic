import React, { useState } from 'react';
import { ConnectionTemplate } from '@/types/features/connections';
import { Search, Plus } from 'lucide-react';
import '@/styles/components/julius-ai-styles.css';

interface ConnectionTemplateGridProps {
  templates: ConnectionTemplate[];
  onSelectTemplate: (template: ConnectionTemplate) => void;
}

export const ConnectionTemplateGrid: React.FC<ConnectionTemplateGridProps> = ({
  templates,
  onSelectTemplate
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  return (
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
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="julius-search-input"
            />
          </div>
        </div>
        
        {/* Template Cards Grid - Julius AI Style */}
        <div className="julius-grid">
          <JuliusTemplateCard
            title="Google Drive"
            description="Analyze your Google Drive files and folders"
            category="Integration"
            type="MCP"
            icon="🗂️"
            onSelect={() => onSelectTemplate({
              id: 'google-drive',
              name: 'Google Drive',
              description: 'Analyze your Google Drive files and folders',
              type: 'file_storage',
              provider: 'google',
              category: 'Integration',
              isPopular: true,
              isOfficial: true,
              tags: ['files', 'storage', 'google']
            } as ConnectionTemplate)}
          />

          <JuliusTemplateCard
            title="Stripe"
            description="Track revenue, subscriptions, and refunds with clean Stripe analytics"
            category="MCP"
            type="MCP"
            icon="💳"
            onSelect={() => onSelectTemplate({
              id: 'stripe',
              name: 'Stripe',
              description: 'Track revenue, subscriptions, and refunds with clean Stripe analytics',
              type: 'payment',
              provider: 'stripe',
              category: 'Payment',
              isPopular: true,
              isOfficial: true,
              tags: ['payment', 'revenue', 'stripe']
            } as ConnectionTemplate)}
          />

          <JuliusTemplateCard
            title="Notion"
            description="Read, update, and organize Notion pages programmatically within Julius"
            category="MCP"
            type="MCP"
            icon="📝"
            onSelect={() => onSelectTemplate({
              id: 'notion',
              name: 'Notion',
              description: 'Read, update, and organize Notion pages programmatically within Julius',
              type: 'file_storage',
              provider: 'notion',
              category: 'Productivity',
              isPopular: true,
              isOfficial: true,
              tags: ['notes', 'productivity', 'notion']
            } as ConnectionTemplate)}
          />

          <JuliusTemplateCard
            title="GitHub"
            description="Search repositories, issues, and pull requests with actionable summaries"
            category="MCP"
            type="MCP"
            icon="🐙"
            onSelect={() => onSelectTemplate({
              id: 'github',
              name: 'GitHub',
              description: 'Search repositories, issues, and pull requests with actionable summaries',
              type: 'api',
              provider: 'github',
              category: 'Development',
              isPopular: true,
              isOfficial: true,
              tags: ['code', 'git', 'github']
            } as ConnectionTemplate)}
          />

          <JuliusTemplateCard
            title="Postgres"
            description="Database"
            category="Database"
            type="Database"
            icon="🐘"
            onSelect={() => onSelectTemplate({
              id: 'postgres',
              name: 'PostgreSQL',
              description: 'Connect to PostgreSQL database',
              type: 'database',
              provider: 'postgresql',
              category: 'Database',
              isPopular: true,
              isOfficial: true,
              tags: ['database', 'sql', 'postgres']
            } as ConnectionTemplate)}
          />
        </div>
      </div>
    </div>
  );
};

// Julius AI Style Template Card
interface JuliusTemplateCardProps {
  title: string;
  description: string;
  category: string;
  type: string;
  icon: string;
  onSelect: () => void;
}

const JuliusTemplateCard: React.FC<JuliusTemplateCardProps> = ({
  title,
  description,
  category,
  type,
  icon,
  onSelect
}) => {
  return (
    <div className="julius-template-card" onClick={onSelect}>
      <div className="julius-template-icon">
        {icon}
      </div>
      
      <div className="mb-4">
        <h3 className="julius-template-title">
          {title}
        </h3>
        <p className="julius-template-description">
          {description}
        </p>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="julius-badge julius-badge-gray">
            {category}
          </span>
          <span className="julius-badge julius-badge-blue">
            {type}
          </span>
        </div>
        
        <button
          className="julius-btn julius-btn-primary"
          onClick={(e) => {
            e.stopPropagation();
            onSelect();
          }}
        >
          <Plus className="h-3 w-3 mr-1" />
          Add
        </button>
      </div>
    </div>
  );
};
