import React, { useState } from 'react';
import {
  Button,
  Textarea,
  Card,
  CardBody,
  Chip,
  Tooltip,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
} from '@heroui/react';
import { Send, Sparkles, Database, Paperclip, Mic, MoreHorizontal } from 'lucide-react';
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
    <div className="p-4 border-t border-divider bg-background/80 backdrop-blur-sm">
      {/* Prompt Manager Modal */}
      {showPrompts && (
        <Card className="absolute bottom-full left-4 right-4 mb-2 shadow-2xl max-h-96 overflow-hidden z-50">
          <CardBody className="p-0">
            <div className="p-4 border-b border-divider bg-gradient-to-r from-primary/5 to-primary/10">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-foreground flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Select a Prompt
                </h3>
                <Button
                  isIconOnly
                  variant="light"
                  size="sm"
                  onPress={() => setShowPrompts(false)}
                >
                  ×
                </Button>
              </div>
            </div>
            <div className="max-h-80 overflow-y-auto">
              <PromptManager compact onSelectPrompt={handlePromptSelect} />
            </div>
          </CardBody>
        </Card>
      )}



      {/* SQL Mode Indicator */}
      {activeConnection && (
        <div className="flex items-center gap-2 mb-3">
          <Chip
            startContent={<Database className="h-3 w-3" />}
            variant="flat"
            color="default"
            size="sm"
          >
            Database: {activeConnection.name}
          </Chip>
          <Button
            variant={isSQL ? "solid" : "bordered"}
            color="primary"
            size="sm"
            onPress={() => setIsSQL(!isSQL)}
          >
            {isSQL ? "SQL Mode" : "Text Mode"}
          </Button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-end gap-3">

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <Tooltip content="Use prompt template">
            <Button
              isIconOnly
              variant={showPrompts ? "flat" : "light"}
              color={showPrompts ? "primary" : "default"}
              onPress={() => setShowPrompts(!showPrompts)}
            >
              <Sparkles className="h-4 w-4" />
            </Button>
          </Tooltip>

          <Tooltip content="Attach file">
            <Button
              isIconOnly
              variant="light"
              color="default"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
          </Tooltip>

          <Dropdown>
            <DropdownTrigger>
              <Button
                isIconOnly
                variant="light"
                color="default"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownTrigger>
            <DropdownMenu>
              <DropdownItem key="voice-input" startContent={<Mic className="h-4 w-4" />}>
                Voice input
              </DropdownItem>
              <DropdownItem key="sql-mode" startContent={<Database className="h-4 w-4" />}>
                SQL mode
              </DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </div>

        {/* Main Input */}
        <div className="flex-1">
          <Textarea
            value={message}
            onValueChange={setMessage}
            onKeyDown={handleKeyPress}
            placeholder={
              isSQL && activeConnection
                ? "Ask in natural language for SQL query..."
                : placeholder
            }
            disabled={disabled}
            minRows={1}
            maxRows={4}
            variant="bordered"
            classNames={{
              input: "resize-none",
              inputWrapper: cn(
                "transition-all duration-200",
                isSQL && "border-primary/50 bg-primary/5"
              )
            }}
            endContent={
              isSQL && (
                <Chip
                  size="sm"
                  variant="flat"
                  color="primary"
                  startContent={<Database className="h-3 w-3" />}
                >
                  SQL
                </Chip>
              )
            }
          />
        </div>

        {/* Send Button */}
        <Button
          type="submit"
          isIconOnly
          color="primary"
          variant={message.trim() && !disabled ? "solid" : "flat"}
          isDisabled={disabled || !message.trim()}
          className="transition-all duration-200"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
};
