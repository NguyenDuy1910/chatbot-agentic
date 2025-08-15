import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Send, Sparkles, Database, Paperclip, X, FileText, Image as ImageIcon, File } from 'lucide-react';
import { Prompt } from '@/types/prompt';
import { DatabaseConnection } from '@/types/database';
import { FileAttachment } from '@/types/chat';
import { PromptManager } from '@/components/PromptManager';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSendMessage: (message: string, attachments?: FileAttachment[]) => void;
  disabled?: boolean;
  placeholder?: string;
  onPromptSelect?: (prompt: Prompt) => void;
  onSQLQuery?: (query: string, connectionId: string) => void;
  activeConnection?: DatabaseConnection | null;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Ask Julius anything...",
  onPromptSelect,
  onSQLQuery,
  activeConnection
}) => {
  const [message, setMessage] = useState('');
  const [showPrompts, setShowPrompts] = useState(false);
  const [isSQL, setIsSQL] = useState(false);
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Generate a simple ID
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    const newAttachments: FileAttachment[] = files.map(file => {
      const url = URL.createObjectURL(file);
      return {
        id: generateId(),
        name: file.name,
        type: file.type,
        size: file.size,
        url,
      };
    });

    setAttachments(prev => [...prev, ...newAttachments]);
    
    // Reset the input value so the same file can be selected again
    if (event.target) {
      event.target.value = '';
    }
  };

  // Remove attachment
  const removeAttachment = (attachmentId: string) => {
    setAttachments(prev => {
      const attachment = prev.find(a => a.id === attachmentId);
      if (attachment?.url) {
        URL.revokeObjectURL(attachment.url);
      }
      return prev.filter(a => a.id !== attachmentId);
    });
  };

  // Get file icon based on type
  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return ImageIcon;
    if (type.includes('text') || type.includes('document')) return FileText;
    return File;
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((message.trim() || attachments.length > 0) && !disabled) {
      if (isSQL && activeConnection && onSQLQuery) {
        onSQLQuery(message.trim(), activeConnection.id);
      } else {
        onSendMessage(message.trim(), attachments.length > 0 ? attachments : undefined);
      }
      setMessage('');
      // Clear attachments and revoke URLs
      attachments.forEach(attachment => {
        if (attachment.url) {
          URL.revokeObjectURL(attachment.url);
        }
      });
      setAttachments([]);
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
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFileUpload}
        accept="image/*,.pdf,.doc,.docx,.txt,.csv,.json,.xml"
      />

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

      {/* File Attachments Preview */}
      {attachments.length > 0 && (
        <div className="border-t bg-background/95 backdrop-blur-sm p-3">
          <div className="flex flex-wrap gap-2">
            {attachments.map((attachment) => {
              const FileIcon = getFileIcon(attachment.type);
              return (
                <div
                  key={attachment.id}
                  className="flex items-center gap-2 bg-muted/50 rounded-lg p-2 border group hover:bg-muted/70 transition-colors"
                >
                  <FileIcon className="h-4 w-4 text-muted-foreground shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-foreground truncate">
                      {attachment.name}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {formatFileSize(attachment.size)}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeAttachment(attachment.id)}
                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/10 hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Enhanced Input Container */}
      <div className="border-t bg-gradient-to-r from-background via-background to-background/95 backdrop-blur-sm">
        <div className="p-4 space-y-3">
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
            {/* File Upload Button */}
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              className="shrink-0 h-12 w-12 rounded-xl border-2 transition-all duration-200 hover:scale-105 hover:bg-muted/50 hover:border-muted-foreground/30"
              title="Attach files"
            >
              <Paperclip className="h-5 w-5" />
            </Button>

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
              disabled={disabled || (!message.trim() && attachments.length === 0)}
              className={cn(
                'shrink-0 h-12 w-12 rounded-xl transition-all duration-200',
                (message.trim() || attachments.length > 0) && !disabled 
                  ? 'bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg shadow-primary/30 hover:scale-105' 
                  : 'bg-muted hover:bg-muted/80'
              )}
            >
              <Send className="h-5 w-5" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};
