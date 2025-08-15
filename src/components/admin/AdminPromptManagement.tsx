import React, { useState, useEffect } from 'react';
import { Prompt, PromptCategory } from '@/types/prompt';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { 
  Table, 
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell 
} from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { 
  Sparkles, 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  BarChart3,
  Search,
  Filter,
  Download,
  Upload
} from 'lucide-react';
import { promptAPI } from '@/lib/promptAPI';

interface AdminPromptManagementProps {
  onPromptSelect?: (prompt: Prompt) => void;
}

export const AdminPromptManagement: React.FC<AdminPromptManagementProps> = ({
  onPromptSelect
}) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    content: '',
    category: 'general' as PromptCategory,
    description: '',
    tags: [] as string[],
    isActive: true
  });

  // Mock usage statistics
  const [promptStats] = useState({
    totalPrompts: 25,
    totalUsage: 1240,
    popularPrompts: [
      { id: '1', title: 'Code Review Helper', usage: 89 },
      { id: '2', title: 'Data Analysis Guide', usage: 76 },
      { id: '3', title: 'Creative Writing Assistant', usage: 65 }
    ],
    categoryDistribution: [
      { category: 'Development', count: 8 },
      { category: 'Writing', count: 6 },
      { category: 'Analysis', count: 5 },
      { category: 'General', count: 6 }
    ]
  });

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    try {
      setIsLoading(true);
      const data = await promptAPI.getPrompts();
      setPrompts(data);
    } catch (error) {
      console.error('Failed to load prompts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || prompt.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(prompts.map(p => p.category)));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingPrompt) {
        const updated = await promptAPI.updatePrompt(editingPrompt.id, formData);
        setPrompts(prev => prev.map(p => p.id === editingPrompt.id ? updated : p));
      } else {
        const newPrompt = await promptAPI.createPrompt(formData);
        setPrompts(prev => [newPrompt, ...prev]);
      }
      resetForm();
    } catch (error) {
      console.error('Failed to save prompt:', error);
    }
  };

  const handleEdit = (prompt: Prompt) => {
    setEditingPrompt(prompt);
    setFormData({
      name: prompt.name,
      content: prompt.content,
      category: prompt.category,
      description: prompt.description || '',
      tags: prompt.tags || [],
      isActive: prompt.isActive
    });
    setShowForm(true);
  };

  const handleDelete = async (promptId: string) => {
    try {
      await promptAPI.deletePrompt(promptId);
      setPrompts(prev => prev.filter(p => p.id !== promptId));
    } catch (error) {
      console.error('Failed to delete prompt:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      content: '',
      category: 'general',
      description: '',
      tags: [],
      isActive: true
    });
    setEditingPrompt(null);
    setShowForm(false);
  };

  const exportPrompts = () => {
    const dataStr = JSON.stringify(prompts, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'prompts.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-foreground">{promptStats.totalPrompts}</div>
                <div className="text-sm text-muted-foreground">Total Prompts</div>
              </div>
              <Sparkles className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-foreground">{promptStats.totalUsage}</div>
                <div className="text-sm text-muted-foreground">Total Usage</div>
              </div>
              <BarChart3 className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-foreground">{categories.length}</div>
                <div className="text-sm text-muted-foreground">Categories</div>
              </div>
              <Filter className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-foreground">
                  {Math.round(promptStats.totalUsage / promptStats.totalPrompts)}
                </div>
                <div className="text-sm text-muted-foreground">Avg Usage</div>
              </div>
              <Eye className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Prompt Management
        </h3>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={exportPrompts} className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export
          </Button>
          <Button variant="outline" className="flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Import
          </Button>
          <Button onClick={() => setShowForm(true)} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            New Prompt
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search prompts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border border-input rounded-md bg-background text-sm"
        >
          <option value="all">All Categories</option>
          {categories.map(category => (
            <option key={category} value={category}>
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Prompt Form Modal */}
      {showForm && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <CardTitle>
              {editingPrompt ? 'Edit Prompt' : 'Create New Prompt'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-foreground">Name</label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Prompt name..."
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground">Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as PromptCategory }))}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                  >
                    <option value="general">General</option>
                    <option value="coding">Coding</option>
                    <option value="creative">Creative</option>
                    <option value="analysis">Analysis</option>
                    <option value="conversation">Conversation</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-foreground">Description</label>
                <Input
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description of what this prompt does..."
                />
              </div>

              <div>
                <label className="text-sm font-medium text-foreground">Content</label>
                <Textarea
                  value={formData.content}
                  onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Enter the prompt content..."
                  rows={4}
                  required
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.isActive}
                    onChange={(e) => setFormData(prev => ({ ...prev, isActive: e.target.checked }))}
                  />
                  <span className="text-sm text-foreground">Active</span>
                </label>
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Cancel
                  </Button>
                  <Button type="submit">
                    {editingPrompt ? 'Update' : 'Create'}
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Prompts Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Prompt</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Usage</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    Loading prompts...
                  </TableCell>
                </TableRow>
              ) : filteredPrompts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    No prompts found
                  </TableCell>
                </TableRow>
              ) : (
                filteredPrompts.map((prompt) => (
                  <TableRow key={prompt.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium text-foreground">{prompt.name}</div>
                        <div className="text-sm text-muted-foreground truncate max-w-xs">
                          {prompt.content}
                        </div>
                        {prompt.description && (
                          <div className="text-xs text-muted-foreground mt-1">
                            {prompt.description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {prompt.category.charAt(0).toUpperCase() + prompt.category.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm font-medium">
                        {Math.floor(Math.random() * 100)} uses
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge className={prompt.isActive ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                        {prompt.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onPromptSelect?.(prompt)}
                          className="h-8 w-8 p-0"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(prompt)}
                          className="h-8 w-8 p-0"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(prompt.id)}
                          className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Popular Prompts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-blue-500" />
            Most Used Prompts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {promptStats.popularPrompts.map((prompt, index) => (
              <div key={prompt.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium">
                    {index + 1}
                  </div>
                  <div>
                    <div className="font-medium text-foreground">{prompt.title}</div>
                    <div className="text-sm text-muted-foreground">{prompt.usage} uses this month</div>
                  </div>
                </div>
                <Badge>{prompt.usage}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
