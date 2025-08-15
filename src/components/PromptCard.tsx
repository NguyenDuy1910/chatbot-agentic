import React from 'react';
import { Prompt } from '@/types/prompt';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Edit3, Trash2, Copy, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PromptCardProps {
  prompt: Prompt;
  onEdit: (prompt: Prompt) => void;
  onDelete: (id: string) => void;
  onUse: (prompt: Prompt) => void;
  onCopy: (content: string) => void;
}

export const PromptCard: React.FC<PromptCardProps> = ({
  prompt,
  onEdit,
  onDelete,
  onUse,
  onCopy
}) => {
  const getCategoryColor = (category: string) => {
    const colors = {
      general: 'bg-blue-100 text-blue-800',
      coding: 'bg-green-100 text-green-800',
      creative: 'bg-purple-100 text-purple-800',
      analysis: 'bg-orange-100 text-orange-800',
      conversation: 'bg-pink-100 text-pink-800',
      custom: 'bg-gray-100 text-gray-800',
    };
    return colors[category as keyof typeof colors] || colors.custom;
  };

  return (
    <div className={cn(
      'bg-card border rounded-lg p-4 space-y-3 transition-all hover:shadow-md',
      !prompt.isActive && 'opacity-60'
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-card-foreground truncate">
              {prompt.name}
            </h3>
            <Badge 
              variant="outline" 
              className={cn('text-xs', getCategoryColor(prompt.category))}
            >
              {prompt.category}
            </Badge>
            {!prompt.isActive && (
              <Badge variant="secondary" className="text-xs">
                Inactive
              </Badge>
            )}
          </div>
          
          {prompt.description && (
            <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
              {prompt.description}
            </p>
          )}
          
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <BarChart3 className="h-3 w-3" />
              Used {prompt.usageCount} times
            </span>
            <span>
              Updated {prompt.updatedAt.toLocaleDateString()}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-1 ml-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onCopy(prompt.content)}
            title="Copy prompt"
          >
            <Copy className="h-3 w-3" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onEdit(prompt)}
            title="Edit prompt"
          >
            <Edit3 className="h-3 w-3" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-destructive hover:text-destructive"
            onClick={() => onDelete(prompt.id)}
            title="Delete prompt"
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <div className="bg-muted/50 rounded-md p-3">
          <p className="text-sm text-card-foreground line-clamp-3">
            {prompt.content}
          </p>
        </div>
        
        {prompt.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {prompt.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                #{tag}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-between items-center pt-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onUse(prompt)}
          disabled={!prompt.isActive}
        >
          Use Prompt
        </Button>
      </div>
    </div>
  );
};
