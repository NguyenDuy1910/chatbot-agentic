import React, { useRef, useEffect } from 'react';
import { Message, FileAttachment } from '@/types/features/chat';
import { Prompt } from '@/types/features/prompt';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { ChatInput } from './ChatInput';
import { Sparkles, Zap, Brain, Database, Square } from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string, attachments?: FileAttachment[]) => void;
  onStop?: () => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onStop
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

  const examplePrompts = [
    { icon: Brain, text: "What can you help me with?", color: "from-blue-500 to-purple-500" },
    { icon: Zap, text: "Explain quantum computing", color: "from-purple-500 to-pink-500" },
    { icon: Database, text: "Write a Python function", color: "from-green-500 to-blue-500" },
  ];

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <div className="border-b border-border/50 bg-gradient-to-r from-background/80 to-muted/20 backdrop-blur-sm p-4 lg:p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="fade-in min-w-0 flex-1">
            <h1 className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              Vikki ChatBot ✨
            </h1>
            <p className="text-xs lg:text-sm text-muted-foreground mt-1">
              Your intelligent assistant with superpowers
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <div className="text-xs text-green-600 font-medium hidden sm:block">Online</div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full p-4 lg:p-8">
            <div className="text-center max-w-2xl mx-auto fade-in">
              <div className="relative w-16 lg:w-20 h-16 lg:h-20 mx-auto mb-4 lg:mb-6">
                <div className="w-16 lg:w-20 h-16 lg:h-20 bg-gradient-to-br from-primary to-primary/60 rounded-2xl flex items-center justify-center shadow-2xl shadow-primary/30 animate-float">
                  <Sparkles className="w-8 lg:w-10 h-8 lg:h-10 text-primary-foreground" />
                </div>
                <div className="absolute -top-1 lg:-top-2 -right-1 lg:-right-2 w-5 lg:w-6 h-5 lg:h-6 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center animate-pulse">
                  <span className="text-xs">✨</span>
                </div>
              </div>
              
              <h2 className="text-2xl lg:text-3xl font-bold mb-2 lg:mb-3 bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                Welcome to Vikki ChatBot
              </h2>
              <p className="text-muted-foreground mb-6 lg:mb-8 text-base lg:text-lg leading-relaxed px-4">
                I'm your AI-powered assistant, ready to help with anything from answering questions 
                to writing code and analyzing data. What would you like to explore today?
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 lg:gap-4 text-sm px-4">
                {examplePrompts.map((prompt, index) => {
                  const Icon = prompt.icon;
                  return (
                    <div 
                      key={index}
                      className="group p-3 lg:p-4 border border-border/50 rounded-xl bg-gradient-to-br from-background to-muted/30 hover:shadow-lg hover:shadow-primary/10 transition-all duration-300 cursor-pointer hover:scale-105 hover:-translate-y-1 scale-in"
                      style={{ animationDelay: `${index * 100}ms` }}
                      onClick={() => onSendMessage(prompt.text)}
                    >
                      <div className={`w-6 lg:w-8 h-6 lg:h-8 rounded-lg bg-gradient-to-r ${prompt.color} flex items-center justify-center mb-2 lg:mb-3 group-hover:scale-110 transition-transform duration-300 mx-auto lg:mx-0`}>
                        <Icon className="w-3 lg:w-4 h-3 lg:h-4 text-white" />
                      </div>
                      <p className="text-foreground font-medium group-hover:text-primary transition-colors duration-300 text-center lg:text-left">
                        {prompt.text}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-0">
            {messages.map((message, index) => (
              <div key={message.id} className="scale-in" style={{ animationDelay: `${index * 50}ms` }}>
                <MessageBubble message={message} />
              </div>
            ))}
            {isLoading && (
              <div className="flex items-center justify-between px-4 py-2">
                <TypingIndicator />
                {onStop && (
                  <Button
                    onClick={onStop}
                    variant="outline"
                    size="sm"
                    className="ml-4 flex items-center gap-2 text-muted-foreground hover:text-foreground"
                  >
                    <Square className="w-3 h-3" />
                    Stop
                  </Button>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput 
        onSendMessage={onSendMessage}
        disabled={isLoading}
        onPromptSelect={handlePromptSelect}
      />
    </div>
  );
};
