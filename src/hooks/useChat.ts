import { useState, useCallback, useEffect } from 'react';
import { useChat as useVercelChat } from 'ai/react';
import { Message, FileAttachment, ChatSession } from '@/types/chat';

// Convert Vercel AI message to our Message type
const convertMessage = (vercelMessage: any): Message => ({
  id: vercelMessage.id,
  content: vercelMessage.content,
  role: vercelMessage.role as 'user' | 'assistant',
  timestamp: new Date(vercelMessage.createdAt || Date.now()),
});

// Convert our Message type to Vercel AI message
const convertToVercelMessage = (message: Message): any => ({
  id: message.id,
  content: message.content,
  role: message.role,
  createdAt: message.timestamp,
});

export interface UseChatOptions {
  sessionId?: string;
  onResponse?: (response: Response) => void;
  onFinish?: (message: Message) => void;
  onError?: (error: Error) => void;
}

export interface UIDataTypes {
  attachments?: FileAttachment[];
}

interface UITools {}

interface UIMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export const useChat = (options: UseChatOptions = {}) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(options.sessionId || null);

  const {
    messages: vercelMessages,
    input,
    handleInputChange,
    handleSubmit: vercelHandleSubmit,
    isLoading,
    error,
    setMessages: setVercelMessages,
    append,
    reload,
    stop,
  } = useVercelChat({
    api: '/api/chat',
    onResponse: options.onResponse,
    onFinish: (message: any) => {
      if (options.onFinish) {
        options.onFinish(convertMessage(message));
      }
    },
    onError: options.onError,
    body: {
      sessionId: currentSessionId,
    },
  });

  // Convert Vercel messages to our format
  const messages = vercelMessages.map(convertMessage);

  // Get current session
  const currentSession = sessions.find(s => s.id === currentSessionId);

  // Generate a simple ID
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Create a new chat session
  const createNewSession = useCallback((): ChatSession => {
    return {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }, []);

  // Handle new chat
  const handleNewChat = useCallback(() => {
    const newSession = createNewSession();
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
    setVercelMessages([]);
  }, [createNewSession, setVercelMessages]);

  // Handle session selection
  const handleSelectSession = useCallback((sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setCurrentSessionId(sessionId);
      setVercelMessages(session.messages.map(convertToVercelMessage));
    }
  }, [sessions, setVercelMessages]);

  // Handle session deletion
  const handleDeleteSession = useCallback((sessionId: string) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
      setVercelMessages([]);
    }
  }, [currentSessionId, setVercelMessages]);

  // Handle sending message with attachments
  const handleSendMessage = useCallback(async (content: string, attachments?: FileAttachment[]) => {
    if (!currentSessionId) {
      handleNewChat();
      return;
    }

    // Update session with new message (user message will be added by Vercel AI)
    setSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? {
            ...session,
            title: session.messages.length === 0 ? content.slice(0, 50) : session.title,
            updatedAt: new Date(),
          }
        : session
    ));

    // Use Vercel AI's append function to send the message
    await append({
      id: generateId(),
      content,
      role: 'user',
      createdAt: new Date(),
    }, {
      data: {
        attachments: attachments ? JSON.stringify(attachments) : '',
      },
    });
  }, [currentSessionId, handleNewChat, append]);

  // Custom submit handler
  const handleSubmit = useCallback((e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!currentSessionId) {
      handleNewChat();
      return;
    }

    // Update session title if it's the first message
    setSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? {
            ...session,
            title: session.messages.length === 0 ? input.slice(0, 50) : session.title,
            updatedAt: new Date(),
          }
        : session
    ));

    vercelHandleSubmit(e, {
      data: {
        sessionId: currentSessionId,
      },
    });
  }, [currentSessionId, handleNewChat, input, vercelHandleSubmit]);

  // Update sessions when messages change
  useEffect(() => {
    if (currentSessionId && messages.length > 0) {
      setSessions(prev => prev.map(session => 
        session.id === currentSessionId 
          ? {
              ...session,
              messages,
              updatedAt: new Date(),
            }
          : session
      ));
    }
  }, [currentSessionId, messages]);

  return {
    // Session management
    sessions,
    currentSessionId,
    currentSession,
    handleNewChat,
    handleSelectSession,
    handleDeleteSession,

    // Chat functionality
    messages,
    input,
    handleInputChange,
    handleSubmit,
    handleSendMessage,
    isLoading,
    error,

    // Streaming controls
    reload,
    stop,
  };
};
