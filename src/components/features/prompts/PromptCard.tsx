import React, { useState } from 'react';
import { Prompt } from '@/types/features/prompt';
import { cn } from '@/lib/utils';
import { Edit2, Trash2, Copy, Play } from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';

export interface PromptCardProps {
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
  onCopy,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div 
      className={cn(
        "group relative rounded-xl overflow-hidden backdrop-blur-sm border border-border/30 transition-all duration-300",
        isExpanded ? "shadow-lg ring-2 ring-primary/20" : "hover:shadow-md hover:scale-102"
      )}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="p-4 bg-gradient-to-r from-background/80 to-muted/20">
        <div className="flex justify-between items-start gap-4">
          <div className="min-w-0 flex-1">
            <h3 className="font-medium text-foreground truncate mb-1">{prompt.name}</h3>
            <div className={cn(
              "text-sm text-muted-foreground overflow-hidden transition-all duration-300",
              isExpanded ? "" : "line-clamp-1"
            )}>
              {prompt.description}
            </div>
          </div>
          <div className="flex gap-1.5 flex-shrink-0">
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "h-7 w-7 transition-all duration-200",
                "text-primary hover:text-primary hover:bg-primary/10",
                !isExpanded && "opacity-0 scale-90 group-hover:opacity-100 group-hover:scale-100"
              )}
              onClick={(e) => {
                e.stopPropagation();
                onUse(prompt);
              }}
            >
              <Play className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "h-7 w-7 transition-all duration-200",
                "text-muted-foreground hover:text-foreground hover:bg-muted/50",
                !isExpanded && "opacity-0 scale-90 group-hover:opacity-100 group-hover:scale-100"
              )}
              onClick={(e) => {
                e.stopPropagation();
                onEdit(prompt);
              }}
            >
              <Edit2 className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "h-7 w-7 transition-all duration-200",
                "text-destructive/80 hover:text-destructive hover:bg-destructive/10",
                !isExpanded && "opacity-0 scale-90 group-hover:opacity-100 group-hover:scale-100"
              )}
              onClick={(e) => {
                e.stopPropagation();
                onDelete(prompt.id);
              }}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        <div className={cn(
          "space-y-3 transition-all duration-300",
          isExpanded ? "opacity-100 mt-4" : "opacity-0 mt-0 pointer-events-none h-0"
        )}>
          {prompt.tags && prompt.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {prompt.tags.map(tag => (
                <span key={tag} className="inline-flex text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                  {tag}
                </span>
              ))}
            </div>
          )}
          
          <div className="text-sm text-muted-foreground">{prompt.content}</div>
          
          <div className="flex items-center justify-between border-t border-border/50 pt-3">
            <div className="text-xs text-muted-foreground">
              Last updated: {prompt.updatedAt.toLocaleDateString()}
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs gap-1.5 text-primary/80 hover:text-primary hover:bg-primary/10"
              onClick={(e) => {
                e.stopPropagation();
                onCopy(prompt.content);
              }}
            >
              <Copy className="h-3 w-3" />
              Copy
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
