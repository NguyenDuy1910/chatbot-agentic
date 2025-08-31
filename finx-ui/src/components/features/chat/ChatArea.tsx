import React, { useRef, useEffect } from 'react';
import { Message, FileAttachment } from '@/types/features/chat';
import { Prompt } from '@/types/features/prompt';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { ChatInput } from './ChatInput';
import { Sparkles, Zap, Brain, Database, Square } from 'lucide-react';
import {
  Card,
  CardBody,
  Button,
  Chip,
  ScrollShadow,
} from '@heroui/react';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string, attachments?: FileAttachment[]) => void;
  onStop?: () => void;
  placeholder?: string;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onStop,
  placeholder = "Ask Vikki anything..."
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handlePromptSelect = (prompt: Prompt) => {
    // When a prompt is selected, you could show it in the input
    // or process it differently based on your needs
    console.log('Prompt selected:', prompt);
  };



  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-background via-background to-default-50/50">
      {/* Header */}
      <div className="border-b border-divider bg-background/80 backdrop-blur-sm p-4 lg:p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="min-w-0 flex-1">
            <h1 className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Vikki ChatBot ✨
            </h1>
            <p className="text-xs lg:text-sm text-default-500 mt-1">
              Your intelligent assistant with superpowers
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Chip
              size="sm"
              variant="flat"
              color="success"
              startContent={<div className="w-2 h-2 bg-success rounded-full animate-pulse" />}
            >
              Online
            </Chip>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollShadow className="flex-1">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full p-8">
            <div className="text-center max-w-2xl mx-auto space-y-6">
              <div className="w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center mx-auto shadow-2xl">
                <Sparkles className="w-10 h-10 text-white" />
              </div>

              <div className="space-y-2">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  Welcome to Vikki ChatBot
                </h1>
                <p className="text-default-600 text-lg">
                  I'm your AI-powered assistant. What would you like to work on today?
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card isPressable isHoverable onPress={() => onSendMessage("What can you help me with?")}>
                  <CardBody className="p-4 text-center">
                    <Brain className="w-8 h-8 text-primary mx-auto mb-2" />
                    <p className="font-medium">What can you help me with?</p>
                  </CardBody>
                </Card>

                <Card isPressable isHoverable onPress={() => onSendMessage("Write a Python function")}>
                  <CardBody className="p-4 text-center">
                    <Zap className="w-8 h-8 text-primary mx-auto mb-2" />
                    <p className="font-medium">Write a Python function</p>
                  </CardBody>
                </Card>

                <Card isPressable isHoverable onPress={() => onSendMessage("Analyze data")}>
                  <CardBody className="p-4 text-center">
                    <Database className="w-8 h-8 text-primary mx-auto mb-2" />
                    <p className="font-medium">Analyze data</p>
                  </CardBody>
                </Card>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-0">
            {messages.map((message, index) => (
              <div key={message.id} className="animate-in slide-in-from-bottom-2 duration-300" style={{ animationDelay: `${index * 50}ms` }}>
                <MessageBubble message={message} />
              </div>
            ))}
            {isLoading && (
              <div className="flex items-center justify-between px-4 py-2">
                <TypingIndicator />
                {onStop && (
                  <Button
                    onPress={onStop}
                    variant="bordered"
                    size="sm"
                    startContent={<Square className="w-3 h-3" />}
                    className="ml-4"
                  >
                    Stop
                  </Button>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </ScrollShadow>

      {/* Input */}
      <ChatInput
        onSendMessage={onSendMessage}
        disabled={isLoading}
        onPromptSelect={handlePromptSelect}
        placeholder={placeholder}
      />
    </div>
  );
};
