import React, { useState } from 'react';
import { Grid, Plus, Search, BookOpen, Play, Edit, Trash2, Star, Clock } from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';

interface Notebook {
  id: string;
  title: string;
  description: string;
  category: string;
  lastModified: Date;
  isStarred: boolean;
  runCount: number;
  status: 'draft' | 'published' | 'archived';
}

const mockNotebooks: Notebook[] = [
  {
    id: '1',
    title: 'Sales Performance Analysis',
    description: 'Comprehensive analysis of Q4 sales data with trend predictions',
    category: 'Sales',
    lastModified: new Date('2024-01-15'),
    isStarred: true,
    runCount: 45,
    status: 'published'
  },
  {
    id: '2',
    title: 'Customer Segmentation Model',
    description: 'Machine learning approach to customer behavior analysis',
    category: 'Marketing',
    lastModified: new Date('2024-01-12'),
    isStarred: false,
    runCount: 23,
    status: 'published'
  },
  {
    id: '3',
    title: 'Financial Risk Assessment',
    description: 'Risk analysis framework for investment decisions',
    category: 'Finance',
    lastModified: new Date('2024-01-10'),
    isStarred: true,
    runCount: 67,
    status: 'draft'
  },
  {
    id: '4',
    title: 'Inventory Optimization',
    description: 'Supply chain optimization using predictive analytics',
    category: 'Operations',
    lastModified: new Date('2024-01-08'),
    isStarred: false,
    runCount: 12,
    status: 'published'
  }
];

export const NotebooksPage: React.FC = () => {
  const [notebooks, setNotebooks] = useState<Notebook[]>(mockNotebooks);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    role: 'admin'
  };

  const categories = ['all', 'Sales', 'Marketing', 'Finance', 'Operations'];

  const filteredNotebooks = notebooks.filter(notebook => {
    const matchesSearch = notebook.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         notebook.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || notebook.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleStarToggle = (id: string) => {
    setNotebooks(prev => prev.map(notebook => 
      notebook.id === id ? { ...notebook, isStarred: !notebook.isStarred } : notebook
    ));
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      published: 'julius-badge julius-badge-green',
      draft: 'julius-badge julius-badge-yellow',
      archived: 'julius-badge julius-badge-gray'
    };
    return statusStyles[status as keyof typeof statusStyles] || 'julius-badge julius-badge-gray';
  };

  return (
    <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Notebooks</h1>
              <p className="text-gray-600 mt-1">Create and manage your analysis notebooks</p>
            </div>
            <Button className="julius-btn julius-btn-primary">
              <Plus className="h-4 w-4 mr-2" />
              New Notebook
            </Button>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1 julius-search-container">
              <Search className="julius-search-icon" />
              <input
                type="text"
                placeholder="Search notebooks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="julius-search-input"
              />
            </div>
            <div className="flex gap-2">
              {categories.map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-blue-100 text-blue-700 border border-blue-200'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Notebooks Grid */}
          <div className="julius-grid">
            {filteredNotebooks.map((notebook) => (
              <div key={notebook.id} className="julius-template-card">
                <div className="flex items-start justify-between mb-4">
                  <div className="julius-template-icon">
                    <BookOpen className="h-8 w-8 text-blue-600" />
                  </div>
                  <button
                    onClick={() => handleStarToggle(notebook.id)}
                    className={`p-1 rounded ${notebook.isStarred ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'}`}
                  >
                    <Star className={`h-4 w-4 ${notebook.isStarred ? 'fill-current' : ''}`} />
                  </button>
                </div>

                <div className="mb-4">
                  <h3 className="julius-template-title">{notebook.title}</h3>
                  <p className="julius-template-description">{notebook.description}</p>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="julius-badge julius-badge-blue">{notebook.category}</span>
                    <span className={getStatusBadge(notebook.status)}>
                      {notebook.status.charAt(0).toUpperCase() + notebook.status.slice(1)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 text-xs text-gray-500">
                    <Play className="h-3 w-3" />
                    <span>{notebook.runCount} runs</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>Modified {notebook.lastModified.toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button size="sm" className="julius-btn julius-btn-primary flex-1">
                    <Play className="h-3 w-3 mr-1" />
                    Run
                  </Button>
                  <Button size="sm" variant="ghost" className="p-2">
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="ghost" className="p-2 text-red-600 hover:text-red-700">
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {filteredNotebooks.length === 0 && (
            <div className="text-center py-12">
              <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No notebooks found</h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || selectedCategory !== 'all' 
                  ? 'Try adjusting your search or filters'
                  : 'Create your first notebook to get started'
                }
              </p>
              <Button className="julius-btn julius-btn-primary">
                <Plus className="h-4 w-4 mr-2" />
                Create Notebook
              </Button>
            </div>
          )}
        </div>
      </div>
  );
};

export default NotebooksPage;
