import React, { useState } from 'react';
import { ChatArea } from '@/components/features/chat';
import { ChatHistory } from '@/components/features/chat/ChatHistory';
import { Message } from '@/types/features/chat';

/**
 * Chat page component - content only
 * Handles the primary chatbot interface
 */
export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);

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

  const handleNewChat = () => {
    setMessages([]);
  };

  const handleSelectConversation = (conversationId: string) => {
    // Mock loading conversation
    console.log('Loading conversation:', conversationId);
    // In real app, load messages from API
  };

  const handleToggleHistory = () => {
    setIsHistoryCollapsed(!isHistoryCollapsed);
  };

  return (
    <div className="h-full flex">
      {/* Chat History Sidebar */}
      <ChatHistory
        isCollapsed={isHistoryCollapsed}
        onToggle={handleToggleHistory}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
      />

      {/* Main Chat Area */}
      <div className="flex-1">
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          placeholder={`Hi ${user.name}! Ask me anything...`}
        />
      </div>
    </div>
  );
};

export default ChatPage;
