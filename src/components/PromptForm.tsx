import React, { useState } from 'react';
import { Prompt, PromptCategory } from '@/types/prompt';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { X, Plus } from 'lucide-react';


interface PromptFormProps {
  prompt?: Prompt;
  onSave: (prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt' | 'usageCount'>) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const PromptForm: React.FC<PromptFormProps> = ({
  prompt,
  onSave,
  onCancel,
  isLoading = false
}) => {
  const [formData, setFormData] = useState({
    name: prompt?.name || '',
    description: prompt?.description || '',
    content: prompt?.content || '',
    category: prompt?.category || 'general' as PromptCategory,
    tags: prompt?.tags || [],
    isActive: prompt?.isActive ?? true,
  });

  const [newTag, setNewTag] = useState('');

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim() && formData.content.trim()) {
      onSave(formData);
    }
  };

  const categories: { value: PromptCategory; label: string }[] = [
    { value: 'general', label: 'General' },
    { value: 'coding', label: 'Coding' },
    { value: 'creative', label: 'Creative' },
    { value: 'analysis', label: 'Analysis' },
    { value: 'conversation', label: 'Conversation' },
    { value: 'custom', label: 'Custom' },
  ];

  return (
    <div className="bg-background border rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">
          {prompt ? 'Edit Prompt' : 'Create New Prompt'}
        </h2>
        <Button variant="ghost" size="icon" onClick={onCancel}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">
              Name *
            </label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter prompt name"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">
              Category
            </label>
            <Select
              value={formData.category}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as PromptCategory }))}
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </Select>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">
            Description
          </label>
          <Input
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Brief description of the prompt"
          />
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">
            Prompt Content *
          </label>
          <Textarea
            value={formData.content}
            onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
            placeholder="Enter your prompt content here..."
            rows={6}
            required
          />
          <p className="text-xs text-muted-foreground mt-1">
            Use {'{variable_name}'} for dynamic variables
          </p>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">
            Tags
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {formData.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="ml-1 hover:bg-destructive/20 rounded-full p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Add a tag"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
            />
            <Button type="button" variant="outline" size="icon" onClick={handleAddTag}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="isActive"
            checked={formData.isActive}
            onChange={(e) => setFormData(prev => ({ ...prev, isActive: e.target.checked }))}
            className="rounded"
          />
          <label htmlFor="isActive" className="text-sm font-medium">
            Active prompt
          </label>
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading || !formData.name.trim() || !formData.content.trim()}>
            {isLoading ? 'Saving...' : (prompt ? 'Update' : 'Create')}
          </Button>
        </div>
      </form>
    </div>
  );
};
