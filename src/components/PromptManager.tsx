import React, { useState, useEffect } from 'react';
import { Prompt, PromptCategory } from '@/types/prompt';
import { PromptCard } from '@/components/PromptCard';
import { PromptForm } from '@/components/PromptForm';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Upload,
  BookOpen,
  Zap,
  TrendingUp 
} from 'lucide-react';
import { promptAPI } from '@/lib/promptAPI';
import { cn } from '@/lib/utils';

interface PromptManagerProps {
  onSelectPrompt?: (prompt: Prompt) => void;
  compact?: boolean;
}

export const PromptManager: React.FC<PromptManagerProps> = ({
  onSelectPrompt,
  compact = false
}) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<PromptCategory | 'all'>('all');
  const [showActiveOnly, setShowActiveOnly] = useState(false);

  // Mock data for demo (replace with actual API calls)
  const generateMockPrompts = (): Prompt[] => [
    {
      id: '1',
      name: 'Code Review Assistant',
      description: 'Helps review code and suggest improvements',
      content: 'You are a senior software engineer. Review this code and provide constructive feedback on:\n\n1. Code quality and best practices\n2. Potential bugs or issues\n3. Performance optimizations\n4. Readability improvements\n\nCode to review:\n{code}',
      category: 'coding',
      tags: ['code-review', 'development', 'quality'],
      isActive: true,
      createdAt: new Date('2024-01-15'),
      updatedAt: new Date('2024-01-20'),
      usageCount: 45
    },
    {
      id: '2',
      name: 'Creative Writing Helper',
      description: 'Assists with creative writing projects',
      content: 'You are a creative writing assistant. Help me with my {writing_type} by:\n\n1. Providing creative suggestions\n2. Improving narrative flow\n3. Enhancing character development\n4. Suggesting plot improvements\n\nTopic: {topic}\nGenre: {genre}\nTarget audience: {audience}',
      category: 'creative',
      tags: ['writing', 'creativity', 'storytelling'],
      isActive: true,
      createdAt: new Date('2024-01-10'),
      updatedAt: new Date('2024-01-18'),
      usageCount: 28
    },
    {
      id: '3',
      name: 'Data Analysis Expert',
      description: 'Analyzes data and provides insights',
      content: 'You are a data analysis expert. Analyze the following data and provide:\n\n1. Key insights and patterns\n2. Statistical summary\n3. Visualization recommendations\n4. Actionable conclusions\n\nData context: {context}\nData: {data}\nGoals: {goals}',
      category: 'analysis',
      tags: ['data', 'analytics', 'insights'],
      isActive: true,
      createdAt: new Date('2024-01-08'),
      updatedAt: new Date('2024-01-22'),
      usageCount: 67
    },
    {
      id: '4',
      name: 'Meeting Summarizer',
      description: 'Summarizes meeting notes and action items',
      content: 'Summarize this meeting transcript and provide:\n\n1. Key discussion points\n2. Decisions made\n3. Action items with owners\n4. Follow-up topics\n\nMeeting transcript:\n{transcript}',
      category: 'general',
      tags: ['meetings', 'summary', 'productivity'],
      isActive: false,
      createdAt: new Date('2024-01-05'),
      updatedAt: new Date('2024-01-15'),
      usageCount: 12
    }
  ];

  useEffect(() => {
    // Initialize with mock data
    setPrompts(generateMockPrompts());
    setIsLoading(false);
  }, []);

  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || prompt.category === selectedCategory;
    const matchesActive = !showActiveOnly || prompt.isActive;
    
    return matchesSearch && matchesCategory && matchesActive;
  });

  const handleSavePrompt = async (promptData: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt' | 'usageCount'>) => {
    try {
      if (editingPrompt) {
        // Update existing prompt
        const updatedPrompt: Prompt = {
          ...editingPrompt,
          ...promptData,
          updatedAt: new Date(),
        };
        setPrompts(prev => prev.map(p => p.id === editingPrompt.id ? updatedPrompt : p));
      } else {
        // Create new prompt
        const newPrompt: Prompt = {
          ...promptData,
          id: Math.random().toString(36).substr(2, 9),
          createdAt: new Date(),
          updatedAt: new Date(),
          usageCount: 0,
        };
        setPrompts(prev => [newPrompt, ...prev]);
      }
      
      setShowForm(false);
      setEditingPrompt(null);
    } catch (error) {
      setError('Failed to save prompt');
    }
  };

  const handleDeletePrompt = async (id: string) => {
    if (confirm('Are you sure you want to delete this prompt?')) {
      setPrompts(prev => prev.filter(p => p.id !== id));
    }
  };

  const handleUsePrompt = (prompt: Prompt) => {
    // Increment usage count
    setPrompts(prev => prev.map(p => 
      p.id === prompt.id 
        ? { ...p, usageCount: p.usageCount + 1 }
        : p
    ));
    
    if (onSelectPrompt) {
      onSelectPrompt(prompt);
    }
  };

  const handleCopyPrompt = (content: string) => {
    navigator.clipboard.writeText(content);
    // You could show a toast notification here
  };

  const handleEditPrompt = (prompt: Prompt) => {
    setEditingPrompt(prompt);
    setShowForm(true);
  };

  const categories: { value: PromptCategory | 'all'; label: string }[] = [
    { value: 'all', label: 'All Categories' },
    { value: 'general', label: 'General' },
    { value: 'coding', label: 'Coding' },
    { value: 'creative', label: 'Creative' },
    { value: 'analysis', label: 'Analysis' },
    { value: 'conversation', label: 'Conversation' },
    { value: 'custom', label: 'Custom' },
  ];

  if (compact) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Input
            placeholder="Search prompts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1"
          />
          <Button onClick={() => setShowForm(true)} size="sm">
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {showForm && (
          <PromptForm
            prompt={editingPrompt || undefined}
            onSave={handleSavePrompt}
            onCancel={() => {
              setShowForm(false);
              setEditingPrompt(null);
            }}
          />
        )}

        <div className="grid gap-3">
          {filteredPrompts.slice(0, 6).map((prompt) => (
            <PromptCard
              key={prompt.id}
              prompt={prompt}
              onEdit={handleEditPrompt}
              onDelete={handleDeletePrompt}
              onUse={handleUsePrompt}
              onCopy={handleCopyPrompt}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="border-b p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <BookOpen className="h-6 w-6" />
              Prompt Manager
            </h1>
            <p className="text-muted-foreground">
              Create, manage, and organize your AI prompts
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Import
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              New Prompt
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Total Prompts</span>
            </div>
            <p className="text-2xl font-bold">{prompts.length}</p>
          </div>
          
          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Active</span>
            </div>
            <p className="text-2xl font-bold">{prompts.filter(p => p.isActive).length}</p>
          </div>
          
          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Most Used</span>
            </div>
            <p className="text-sm font-medium">
              {prompts.reduce((max, p) => p.usageCount > max.usageCount ? p : max, prompts[0])?.name || 'None'}
            </p>
          </div>
          
          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Categories</span>
            </div>
            <p className="text-2xl font-bold">{new Set(prompts.map(p => p.category)).size}</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3">
          <div className="flex-1 min-w-0">
            <Input
              placeholder="Search prompts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          
          <Select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as PromptCategory | 'all')}
          >
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </Select>
          
          <Button
            variant={showActiveOnly ? 'default' : 'outline'}
            onClick={() => setShowActiveOnly(!showActiveOnly)}
            className="whitespace-nowrap"
          >
            Active Only
          </Button>
        </div>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <PromptForm
              prompt={editingPrompt || undefined}
              onSave={handleSavePrompt}
              onCancel={() => {
                setShowForm(false);
                setEditingPrompt(null);
              }}
            />
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-muted-foreground">Loading prompts...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-32">
            <div className="text-destructive">{error}</div>
          </div>
        ) : filteredPrompts.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-center">
            <div>
              <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No prompts found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || selectedCategory !== 'all' 
                  ? 'Try adjusting your search or filters'
                  : 'Create your first prompt to get started'
                }
              </p>
              {!searchTerm && selectedCategory === 'all' && (
                <Button onClick={() => setShowForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Prompt
                </Button>
              )}
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredPrompts.map((prompt) => (
              <PromptCard
                key={prompt.id}
                prompt={prompt}
                onEdit={handleEditPrompt}
                onDelete={handleDeletePrompt}
                onUse={handleUsePrompt}
                onCopy={handleCopyPrompt}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
