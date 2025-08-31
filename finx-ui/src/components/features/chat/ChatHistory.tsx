import React, { useState } from 'react';
import {
  Card,
  CardBody,
  Button,
  Chip,
  Divider,
  ScrollShadow,
  Tooltip,
} from '@heroui/react';
import {
  MessageSquare,
  Plus,
  Search,
  Clock,
  ChevronLeft,
  ChevronRight,
  Trash2,
  Edit3,
} from 'lucide-react';

interface ChatConversation {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
  messageCount: number;
  isActive?: boolean;
}

interface ChatHistoryProps {
  isCollapsed: boolean;
  onToggle: () => void;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({
  isCollapsed,
  onToggle,
  onNewChat,
  onSelectConversation,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Mock conversation data
  const conversations: ChatConversation[] = [
    {
      id: '1',
      title: 'Python Data Analysis',
      preview: 'How to analyze CSV data with pandas...',
      timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
      messageCount: 12,
      isActive: true,
    },
    {
      id: '2',
      title: 'React Component Design',
      preview: 'Best practices for creating reusable components...',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
      messageCount: 8,
    },
    {
      id: '3',
      title: 'Database Optimization',
      preview: 'SQL query performance tuning strategies...',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
      messageCount: 15,
    },
    {
      id: '4',
      title: 'Machine Learning Basics',
      preview: 'Introduction to neural networks and deep learning...',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
      messageCount: 20,
    },
    {
      id: '5',
      title: 'API Development',
      preview: 'RESTful API design principles and implementation...',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
      messageCount: 6,
    },
  ];

  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.preview.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60));
      return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  if (isCollapsed) {
    return (
      <div className="w-16 h-full bg-background border-r border-divider flex flex-col">
        <div className="p-3 border-b border-divider">
          <Tooltip content="Expand Chat History" placement="right">
            <Button
              isIconOnly
              variant="light"
              onPress={onToggle}
              className="w-full"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </Tooltip>
        </div>
        
        <div className="flex-1 p-2 space-y-2 overflow-y-auto">
          <Tooltip content="New Chat" placement="right">
            <Button
              isIconOnly
              color="primary"
              variant="flat"
              onPress={onNewChat}
              className="w-full"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </Tooltip>
          
          {conversations.slice(0, 5).map((conv) => (
            <Tooltip key={conv.id} content={conv.title} placement="right">
              <Button
                isIconOnly
                variant={conv.isActive ? "flat" : "light"}
                color={conv.isActive ? "primary" : "default"}
                onPress={() => onSelectConversation(conv.id)}
                className="w-full"
              >
                <MessageSquare className="h-4 w-4" />
              </Button>
            </Tooltip>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 h-full bg-background border-r border-divider flex flex-col">
      <div className="p-4 pb-3 border-b border-divider">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold">Chat History</h3>
          </div>
          <Button
            isIconOnly
            variant="light"
            size="sm"
            onPress={onToggle}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="p-4 border-b border-divider">
        <Button
          color="primary"
          variant="flat"
          startContent={<Plus className="h-4 w-4" />}
          onPress={onNewChat}
          className="w-full justify-start"
        >
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-hidden">
        <ScrollShadow className="h-full">
          <div className="p-4 space-y-3">
            {filteredConversations.map((conversation) => (
              <Card
                key={conversation.id}
                isPressable
                isHoverable
                className={`cursor-pointer transition-all duration-200 ${
                  conversation.isActive 
                    ? 'bg-primary-50 border-primary-200 shadow-md' 
                    : 'hover:bg-default-50'
                }`}
                onPress={() => onSelectConversation(conversation.id)}
              >
                <CardBody className="p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-foreground truncate">
                        {conversation.title}
                      </h4>
                      <p className="text-xs text-default-500 mt-1 line-clamp-2">
                        {conversation.preview}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Chip
                          size="sm"
                          variant="flat"
                          color="default"
                          startContent={<Clock className="h-3 w-3" />}
                        >
                          {formatTimestamp(conversation.timestamp)}
                        </Chip>
                        <Chip size="sm" variant="flat" color="primary">
                          {conversation.messageCount} msgs
                        </Chip>
                      </div>
                    </div>
                    
                    <div className="flex flex-col gap-1">
                      <Button
                        isIconOnly
                        size="sm"
                        variant="light"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Edit3 className="h-3 w-3" />
                      </Button>
                      <Button
                        isIconOnly
                        size="sm"
                        variant="light"
                        color="danger"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        </ScrollShadow>
      </div>

      <div className="p-4 border-t border-divider">
        <div className="text-xs text-default-500 text-center">
          {filteredConversations.length} conversations
        </div>
      </div>
    </div>
  );
};
