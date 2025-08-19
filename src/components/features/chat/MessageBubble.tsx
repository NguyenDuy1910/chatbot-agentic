import React from 'react';
import { Message } from '@/types/features/chat';
import { cn } from '@/lib/utils';
import { User, Bot, Sparkles, Download, FileText, Image as ImageIcon, File, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import {
  Card,
  CardBody,
  Button,
  Avatar,
  Chip,
  Tooltip,
} from '@heroui/react';

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

  const handleCopyMessage = () => {
    navigator.clipboard.writeText(message.content);
  };

  return (
    <div className={cn(
      'flex items-start gap-3 p-4 group hover:bg-default-50/50 transition-colors duration-200',
      isUser ? 'flex-row-reverse' : ''
    )}>
      <div className="relative flex-shrink-0">
        <Avatar
          icon={isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
          className={cn(
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground'
          )}
          size="sm"
        />
        {!isUser && (
          <div className="absolute -top-1 -right-1">
            <Sparkles className="h-3 w-3 text-primary animate-pulse" />
          </div>
        )}
      </div>

      <div className={cn(
        'flex-1 space-y-3 overflow-hidden max-w-3xl',
        isUser ? 'flex flex-col items-end' : 'flex flex-col items-start'
      )}>
        {/* Message content */}
        {message.content && (
          <Card
            className={cn(
              'max-w-lg transition-all duration-200 hover:shadow-md',
              isUser
                ? 'bg-primary text-primary-foreground'
                : 'bg-default-100 border border-divider'
            )}
          >
            <CardBody className="p-4">
              <div className="whitespace-pre-wrap break-words leading-relaxed text-sm">
                {message.content}
              </div>

              {/* Message actions - Only for AI messages */}
              {!isUser && (
                <div className="flex items-center gap-1 mt-3 pt-2 border-t border-divider/50">
                  <Tooltip content="Copy message" placement="top">
                    <Button
                      isIconOnly
                      size="sm"
                      variant="light"
                      onPress={handleCopyMessage}
                      className="h-7 w-7 text-default-400 hover:text-default-600 hover:bg-default-100"
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </Button>
                  </Tooltip>

                  <Tooltip content="Good response" placement="top">
                    <Button
                      isIconOnly
                      size="sm"
                      variant="light"
                      className="h-7 w-7 text-default-400 hover:text-success hover:bg-success-50"
                    >
                      <ThumbsUp className="h-3.5 w-3.5" />
                    </Button>
                  </Tooltip>

                  <Tooltip content="Poor response" placement="top">
                    <Button
                      isIconOnly
                      size="sm"
                      variant="light"
                      className="h-7 w-7 text-default-400 hover:text-danger hover:bg-danger-50"
                    >
                      <ThumbsDown className="h-3.5 w-3.5" />
                    </Button>
                  </Tooltip>
                </div>
              )}
            </CardBody>
          </Card>
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

        {/* Timestamp */}
        <div className={cn(
          'px-2',
          isUser ? 'text-right' : 'text-left'
        )}>
          <Chip
            size="sm"
            variant="light"
            className="text-xs text-default-500"
          >
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Chip>
        </div>
      </div>
    </div>
  );
};
