import React from 'react';
import '@/styles/components/julius-ai-styles.css';

interface TemplateCard {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  type: string;
  runs?: number;
  isPopular?: boolean;
}

interface JuliusTemplateCardsProps {
  searchTerm?: string;
  onTemplateSelect?: (template: TemplateCard) => void;
}

const templateCards: TemplateCard[] = [
  {
    id: 'sales-crm',
    title: 'Sales CRM Closed-Lost Report',
    description: 'This notebook provides step-by-step instructions...',
    icon: '📊',
    category: 'Analysis',
    type: 'Notebook',
    runs: 1078,
    isPopular: true
  },
  {
    id: 'acquisition-channel',
    title: 'Acquisition Channel Efficiency Analysis',
    description: 'Acquisition Channel Efficiency Analysis...',
    icon: '📈',
    category: 'Marketing',
    type: 'Analysis',
    runs: 967
  },
  {
    id: 'significance-testing',
    title: 'Significance Testing',
    description: 'Run significance test on columns in a sheet (e.g., A/B test results)...',
    icon: '🧪',
    category: 'Testing',
    type: 'Analysis',
    runs: 1876
  },
  {
    id: 'customer-segmentation',
    title: 'Customer Segmentation Analysis',
    description: 'Customer segmentation Analysis groups customer...',
    icon: '👥',
    category: 'Customer',
    type: 'Analysis',
    runs: 1843
  },
  {
    id: 'financial-analysis',
    title: 'Financial Performance Analysis',
    description: 'Analyze financial metrics and performance indicators...',
    icon: '💰',
    category: 'Finance',
    type: 'Analysis',
    runs: 756
  },
  {
    id: 'user-behavior',
    title: 'User Behavior Analytics',
    description: 'Track and analyze user behavior patterns...',
    icon: '📱',
    category: 'Analytics',
    type: 'Notebook',
    runs: 892
  },
  {
    id: 'inventory-management',
    title: 'Inventory Management Report',
    description: 'Monitor inventory levels and optimize stock management...',
    icon: '📦',
    category: 'Operations',
    type: 'Report',
    runs: 634
  },
  {
    id: 'social-media',
    title: 'Social Media Performance',
    description: 'Analyze social media engagement and reach metrics...',
    icon: '📱',
    category: 'Marketing',
    type: 'Analysis',
    runs: 523
  }
];

export const JuliusTemplateCards: React.FC<JuliusTemplateCardsProps> = ({
  searchTerm = '',
  onTemplateSelect
}) => {
  const filteredTemplates = templateCards.filter(template =>
    template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleTemplateClick = (template: TemplateCard) => {
    if (onTemplateSelect) {
      onTemplateSelect(template);
    } else {
      // Default action - could navigate to template or open modal
      console.log('Selected template:', template);
    }
  };

  return (
    <div className="julius-grid">
      {filteredTemplates.map((template) => (
        <div 
          key={template.id} 
          className="julius-template-card"
          onClick={() => handleTemplateClick(template)}
        >
          <div className="julius-template-icon">{template.icon}</div>
          <div className="mb-4">
            <h3 className="julius-template-title">{template.title}</h3>
            <p className="julius-template-description">
              {template.description}
            </p>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="julius-badge julius-badge-gray">{template.category}</span>
              <span className="julius-badge julius-badge-blue">{template.type}</span>
              {template.isPopular && (
                <span className="julius-badge julius-badge-yellow">Popular</span>
              )}
            </div>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <span>{template.runs} runs</span>
            </div>
          </div>
        </div>
      ))}
      
      {filteredTemplates.length === 0 && (
        <div className="col-span-full text-center py-12">
          <div className="text-gray-400 text-lg mb-2">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-600">
            Try adjusting your search terms or browse all available templates.
          </p>
        </div>
      )}
    </div>
  );
};

export default JuliusTemplateCards;
