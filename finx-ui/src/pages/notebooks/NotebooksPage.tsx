import React, { useState } from 'react';
import { Plus, Search, BookOpen, Play, Edit, Trash2, Star, Clock, MoreVertical } from 'lucide-react';
import {
  Button,
  Card,
  CardBody,
  Input,
  Chip,
  Tabs,
  Tab,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Tooltip,
} from '@heroui/react';

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'success';
      case 'draft':
        return 'warning';
      case 'archived':
        return 'default';
      default:
        return 'default';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Sales':
        return 'primary';
      case 'Marketing':
        return 'secondary';
      case 'Finance':
        return 'success';
      case 'Operations':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Notebooks
              </h1>
              <p className="text-default-600 mt-2 text-lg">Create and manage your analysis notebooks</p>
            </div>
            <Button 
              color="primary" 
              size="lg"
              startContent={<Plus className="h-5 w-5" />}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
            >
              New Notebook
            </Button>
          </div>

          <Card className="mb-8 bg-white/70 backdrop-blur-sm border-0 shadow-lg">
            <CardBody className="p-6">
              <div className="flex flex-col lg:flex-row gap-6">
                <div className="flex-1">
                  <Input
                    placeholder="Search notebooks..."
                    value={searchTerm}
                    onValueChange={setSearchTerm}
                    startContent={<Search className="h-4 w-4 text-default-400" />}
                    variant="bordered"
                    size="lg"
                    classNames={{
                      input: "text-sm",
                      inputWrapper: "bg-white/50 border-default-200 hover:border-primary-300 focus-within:border-primary-500"
                    }}
                  />
                </div>
                
                <div className="flex-shrink-0">
                  <Tabs
                    selectedKey={selectedCategory}
                    onSelectionChange={(key) => setSelectedCategory(key as string)}
                    variant="bordered"
                    color="primary"
                    classNames={{
                      tabList: "bg-white/50 backdrop-blur-sm",
                      tab: "data-[selected=true]:bg-primary-500 data-[selected=true]:text-white",
                    }}
                  >
                    {categories.map(category => (
                      <Tab 
                        key={category} 
                        title={category.charAt(0).toUpperCase() + category.slice(1)}
                      />
                    ))}
                  </Tabs>
                </div>
              </div>
            </CardBody>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredNotebooks.map((notebook) => (
              <Card 
                key={notebook.id} 
                className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]"
                isPressable
              >
                <CardBody className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
                      <BookOpen className="h-6 w-6" />
                    </div>
                    <Tooltip content={notebook.isStarred ? "Remove from favorites" : "Add to favorites"}>
                      <Button
                        isIconOnly
                        variant="light"
                        size="sm"
                        onPress={() => handleStarToggle(notebook.id)}
                        className={`${notebook.isStarred ? 'text-warning-500' : 'text-default-400 hover:text-warning-500'} transition-colors`}
                      >
                        <Star className={`h-4 w-4 ${notebook.isStarred ? 'fill-current' : ''}`} />
                      </Button>
                    </Tooltip>
                  </div>

                  <div className="mb-4">
                    <h3 className="text-lg font-bold text-foreground mb-2 group-hover:text-primary-600 transition-colors truncate" title={notebook.title}>
                      {notebook.title}
                    </h3>
                    <p className="text-sm text-default-600 line-clamp-2 overflow-hidden" style={{
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      lineHeight: '1.4em',
                      maxHeight: '2.8em'
                    }} title={notebook.description}>
                      {notebook.description}
                    </p>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Chip
                        size="sm"
                        variant="flat"
                        color={getCategoryColor(notebook.category)}
                        className="font-medium"
                      >
                        {notebook.category}
                      </Chip>
                      <Chip
                        size="sm"
                        variant="flat"
                        color={getStatusColor(notebook.status)}
                        className="font-medium"
                      >
                        {notebook.status.charAt(0).toUpperCase() + notebook.status.slice(1)}
                      </Chip>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-default-500">
                      <Play className="h-3 w-3" />
                      <span>{notebook.runCount} runs</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-default-500 mb-6">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>Modified {notebook.lastModified.toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button 
                      size="sm" 
                      color="primary"
                      variant="solid"
                      startContent={<Play className="h-3 w-3" />}
                      className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold"
                    >
                      Run
                    </Button>
                    
                    <Dropdown>
                      <DropdownTrigger>
                        <Button
                          isIconOnly
                          size="sm"
                          variant="flat"
                          color="default"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownTrigger>
                      <DropdownMenu>
                        <DropdownItem
                          key="edit"
                          startContent={<Edit className="h-4 w-4" />}
                        >
                          Edit
                        </DropdownItem>
                        <DropdownItem
                          key="delete"
                          className="text-danger"
                          color="danger"
                          startContent={<Trash2 className="h-4 w-4" />}
                        >
                          Delete
                        </DropdownItem>
                      </DropdownMenu>
                    </Dropdown>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>

          {filteredNotebooks.length === 0 && (
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardBody className="text-center py-16">
                <div className="p-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                  <BookOpen className="h-10 w-10" />
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3">No notebooks found</h3>
                <p className="text-default-600 mb-8 max-w-md mx-auto">
                  {searchTerm || selectedCategory !== 'all'
                    ? 'Try adjusting your search or filters to find what you\'re looking for'
                    : 'Create your first notebook to get started with your analysis journey'
                  }
                </p>
                <Button
                  color="primary"
                  size="lg"
                  startContent={<Plus className="h-5 w-5" />}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  Create Notebook
                </Button>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotebooksPage;
