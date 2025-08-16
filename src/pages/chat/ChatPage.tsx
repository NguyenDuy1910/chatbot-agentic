import React, { useState } from 'react';
import { ChatArea, ChatInput } from '@/components/features/chat';
import { Message } from '@/types/features/chat';

/**
 * Chat page component - content only
 * Handles the primary chatbot interface
 */
export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Mock user data - replace with actual user context
  const user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    role: 'admin'
  };

  const handleSendMessage = (content: string, attachments?: any[]) => {
    const newMessage: Message = {
      id: Math.random().toString(36).substring(2, 11),
      content,
      role: 'user',
      timestamp: new Date(),
      attachments
    };

    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: Math.random().toString(36).substring(2, 11),
        content: `Hi ${user.name}! I received your message: "${content}". How can I help you today?`,
        role: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-hidden">
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </div>
      <div className="border-t border-gray-200 bg-white p-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          placeholder={`Hi ${user.name}! Ask me anything...`}
        />
      </div>
    </div>
  );
};

export default ChatPage;
