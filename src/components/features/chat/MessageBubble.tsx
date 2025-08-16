import React from 'react';
import { Message } from '@/types/features/chat';
import { cn } from '@/lib/utils';
import { User, Bot, Sparkles, Download, FileText, Image as ImageIcon, File } from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

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

  // Handle file download
  const handleFileDownload = (attachment: any) => {
    const link = document.createElement('a');
    link.href = attachment.url;
    link.download = attachment.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className={cn(
      'flex items-start space-x-3 p-4 fade-in',
      isUser ? 'flex-row-reverse space-x-reverse' : ''
    )}>
      <div className={cn(
        'flex h-10 w-10 shrink-0 select-none items-center justify-center rounded-xl shadow-lg transition-all duration-300 hover:scale-110',
        isUser 
          ? 'bg-gradient-to-br from-primary to-primary/80 text-primary-foreground shadow-primary/30' 
          : 'bg-gradient-to-br from-muted to-muted/80 shadow-muted/30'
      )}>
        {isUser ? (
          <User className="h-5 w-5" />
        ) : (
          <div className="relative">
            <Bot className="h-5 w-5" />
            <Sparkles className="h-2 w-2 absolute -top-1 -right-1 text-primary animate-pulse" />
          </div>
        )}
      </div>
      
      <div className={cn(
        'flex-1 space-y-2 overflow-hidden max-w-3xl',
        isUser ? 'text-right' : ''
      )}>
        {/* Message content */}
        {message.content && (
          <div className={cn(
            'inline-block rounded-2xl px-4 py-3 text-sm shadow-md transition-all duration-300 hover:shadow-lg hover:scale-102',
            isUser
              ? 'bg-gradient-to-br from-primary to-primary/90 text-primary-foreground shadow-primary/20'
              : 'bg-gradient-to-br from-muted to-muted/80 shadow-muted/30 border border-border/50'
          )}>
            <div className="whitespace-pre-wrap break-words leading-relaxed">
              {message.content}
            </div>
          </div>
        )}

        {/* File attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className={cn(
            'space-y-2',
            isUser ? 'flex flex-col items-end' : 'flex flex-col items-start'
          )}>
            {message.attachments.map((attachment) => {
              const FileIcon = getFileIcon(attachment.type);
              const isImage = attachment.type.startsWith('image/');
              
              return (
                <div
                  key={attachment.id}
                  className={cn(
                    'max-w-sm rounded-xl border shadow-md transition-all duration-300 hover:shadow-lg',
                    isUser
                      ? 'bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20'
                      : 'bg-gradient-to-br from-muted/50 to-muted/30 border-border/50'
                  )}
                >
                  {isImage ? (
                    <div className="relative">
                      <img
                        src={attachment.url}
                        alt={attachment.name}
                        className="w-full h-48 object-cover rounded-t-xl"
                      />
                      <div className="absolute top-2 right-2">
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleFileDownload(attachment)}
                          className="h-8 w-8 p-0 bg-black/50 hover:bg-black/70 text-white border-none"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="p-3 border-t bg-background/90 backdrop-blur-sm rounded-b-xl">
                        <div className="flex items-center justify-between">
                          <div className="min-w-0 flex-1">
                            <div className="text-sm font-medium text-foreground truncate">
                              {attachment.name}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {formatFileSize(attachment.size)}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3">
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg',
                          isUser
                            ? 'bg-primary/20 text-primary'
                            : 'bg-muted text-muted-foreground'
                        )}>
                          <FileIcon className="h-5 w-5" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="text-sm font-medium text-foreground truncate">
                            {attachment.name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {formatFileSize(attachment.size)}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleFileDownload(attachment)}
                          className="h-8 w-8 p-0 hover:bg-muted/50"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
        
        <div className={cn(
          'text-xs text-muted-foreground/70 font-medium',
          isUser ? 'text-right' : ''
        )}>
          {message.timestamp.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
};
