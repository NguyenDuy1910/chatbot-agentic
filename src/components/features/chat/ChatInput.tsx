import React, { useState } from 'react';
import { Button } from '@/components/shared/ui/Button';
import { Input } from '@/components/shared/ui/Input';
import { Send, Sparkles, Database } from 'lucide-react';
import { Prompt } from '@/types/features/prompt';
import { DatabaseConnection } from '@/types/features/database';
import { PromptManager } from '@/components/features/prompts/PromptManager';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  onPromptSelect?: (prompt: Prompt) => void;
  onSQLQuery?: (query: string, connectionId: string) => void;
  activeConnection?: DatabaseConnection | null;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Ask Vikki anything...",
  onPromptSelect,
  onSQLQuery,
  activeConnection
}) => {
  const [message, setMessage] = useState('');
  const [showPrompts, setShowPrompts] = useState(false);
  const [isSQL, setIsSQL] = useState(false);



  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      if (isSQL && activeConnection && onSQLQuery) {
        onSQLQuery(message.trim(), activeConnection.id);
      } else {
        onSendMessage(message.trim());
      }
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handlePromptSelect = (prompt: Prompt) => {
    setMessage(prompt.content);
    setShowPrompts(false);
    if (onPromptSelect) {
      onPromptSelect(prompt);
    }
  };

  return (
    <div className="relative">
      {/* Prompt Manager Modal */}
      {showPrompts && (
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-background border rounded-xl shadow-2xl max-h-96 overflow-hidden z-50 backdrop-blur-sm border-border/50">
          <div className="p-4 border-b bg-gradient-to-r from-primary/5 to-primary/10">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Select a Prompt
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowPrompts(false)}
                className="hover:bg-muted/80 h-8 w-8 p-0 rounded-full"
              >
                ×
              </Button>
            </div>
          </div>
          <div className="max-h-80 overflow-y-auto custom-scrollbar">
            <PromptManager compact onSelectPrompt={handlePromptSelect} />
          </div>
        </div>
      )}



          {/* SQL Mode Indicator */}
          {activeConnection && (
            <div className="flex items-center gap-2 text-xs">
              <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-muted/50">
                <Database className="h-3 w-3" />
                <span className="text-muted-foreground">Database:</span>
                <span className="font-medium">{activeConnection.name}</span>
              </div>
              <Button
                variant={isSQL ? "default" : "outline"}
                size="sm"
                onClick={() => setIsSQL(!isSQL)}
                className="h-6 px-2 text-xs"
              >
                {isSQL ? "SQL Mode" : "Text Mode"}
              </Button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex items-end gap-3">

            {/* Prompt Button */}
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => setShowPrompts(!showPrompts)}
              className={cn(
                'shrink-0 h-12 w-12 rounded-xl border-2 transition-all duration-200 hover:scale-105',
                showPrompts 
                  ? 'bg-primary/10 text-primary border-primary/30 shadow-lg shadow-primary/20' 
                  : 'hover:bg-primary/5 hover:border-primary/20'
              )}
              title="Use prompt template"
            >
              <Sparkles className="h-5 w-5" />
            </Button>

            {/* Main Input */}
            <div className="flex-1 relative">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  isSQL && activeConnection 
                    ? "Ask in natural language for SQL query..." 
                    : placeholder
                }
                disabled={disabled}
                className={cn(
                  "min-h-12 pr-14 rounded-xl border-2 transition-all duration-200 resize-none",
                  "focus:border-primary/50 focus:ring-2 focus:ring-primary/20 focus:ring-offset-0",
                  "hover:border-primary/30",
                  isSQL && "border-blue-200 bg-blue-50/30 placeholder:text-blue-600/70"
                )}
              />
              
              {/* Message Type Indicator */}
              {isSQL && (
                <div className="absolute right-14 top-1/2 -translate-y-1/2">
                  <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-xs">
                    <Database className="h-3 w-3" />
                    SQL
                  </div>
                </div>
              )}
            </div>

            {/* Send Button */}
            <Button
              type="submit"
              size="icon"
              disabled={disabled || !message.trim()}
              className={cn(
                'shrink-0 h-12 w-12 rounded-xl transition-all duration-200',
                message.trim() && !disabled 
                  ? 'bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg shadow-primary/30 hover:scale-105' 
                  : 'bg-muted hover:bg-muted/80'
              )}
            >
              <Send className="h-5 w-5" />
            </Button>
          </form>
    </div>
  );
};
