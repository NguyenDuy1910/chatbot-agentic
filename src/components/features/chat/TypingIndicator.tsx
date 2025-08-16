import React from 'react';
import { cn } from '@/lib/utils';

interface TypingIndicatorProps {
  className?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ className }) => {
  return (
    <div className={cn('flex items-center space-x-1 p-3', className)}>
      <div className="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <span className="text-sm text-muted-foreground ml-2">Vikki is thinking...</span>
    </div>
  );
};
