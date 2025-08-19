import React from 'react';
import { cn } from '@/lib/utils';
import { Avatar, Chip } from '@heroui/react';
import { Bot, Sparkles } from 'lucide-react';

interface TypingIndicatorProps {
  className?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ className }) => {
  return (
    <div className={cn('flex items-center gap-3 p-4', className)}>
      <Avatar
        icon={<Bot className="h-5 w-5" />}
        className="bg-secondary text-secondary-foreground flex-shrink-0"
        size="sm"
      />
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
        <Chip
          size="sm"
          variant="flat"
          color="primary"
          startContent={<Sparkles className="h-3 w-3 animate-pulse" />}
        >
          Vikki is thinking...
        </Chip>
      </div>
    </div>
  );
};
