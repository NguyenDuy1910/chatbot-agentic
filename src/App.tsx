import { useState, useEffect } from 'react';
import { ChatSession, Message, FileAttachment } from '@/types/chat';
import { Sidebar } from '@/components/Sidebar';
import { ChatArea } from '@/components/ChatArea';

function App() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const currentSession = sessions.find(s => s.id === currentSessionId);
  const messages = currentSession?.messages || [];

  // Generate a simple ID
  const generateId = () => Math.random().toString(36).substr(2, 9);

  // Create a new chat session
  const createNewSession = (): ChatSession => {
    return {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  };

  // Handle new chat
  const handleNewChat = () => {
    const newSession = createNewSession();
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
  };

  // Handle session selection
  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  // Handle session deletion
  const handleDeleteSession = (sessionId: string) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
    }
  };

  // Handle sending message
  const handleSendMessage = async (content: string, attachments?: FileAttachment[]) => {
    if (!currentSessionId) {
      handleNewChat();
      return;
    }

    const userMessage: Message = {
      id: generateId(),
      content,
      role: 'user',
      timestamp: new Date(),
      attachments: attachments || undefined,
    };

    // Add user message
    setSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? {
            ...session,
            messages: [...session.messages, userMessage],
            title: session.messages.length === 0 ? content.slice(0, 50) : session.title,
            updatedAt: new Date(),
          }
        : session
    ));

    setIsLoading(true);

    try {
      // Simulate API call - replace with actual backend integration
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      let responseContent = `I understand you're asking about: "${content}". This is a demo response from Julius AI.`;
      
      if (attachments && attachments.length > 0) {
        const fileNames = attachments.map(att => att.name).join(', ');
        responseContent += ` I can see you've uploaded ${attachments.length} file${attachments.length > 1 ? 's' : ''}: ${fileNames}. In a real implementation, I would analyze these files and provide insights based on their content.`;
      } else {
        responseContent += ` In a real implementation, this would be connected to your backend API that processes the message and returns an appropriate AI response.`;
      }
      
      const assistantMessage: Message = {
        id: generateId(),
        content: responseContent,
        role: 'assistant',
        timestamp: new Date(),
      };

      // Add assistant message
      setSessions(prev => prev.map(session => 
        session.id === currentSessionId 
          ? {
              ...session,
              messages: [...session.messages, assistantMessage],
              updatedAt: new Date(),
            }
          : session
      ));

    } catch (error) {
      console.error('Failed to send message:', error);
      // Handle error - you could show a toast notification here
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize with a default session if none exist
  useEffect(() => {
    if (sessions.length === 0) {
      handleNewChat();
    }
  }, []);

  return (
    <div className="flex h-screen bg-gradient-to-br from-background via-background to-muted/10 overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-32 lg:w-64 h-32 lg:h-64 bg-primary/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-1/3 right-1/4 w-24 lg:w-48 h-24 lg:h-48 bg-purple-500/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 right-1/3 w-16 lg:w-32 h-16 lg:h-32 bg-blue-500/5 rounded-full blur-2xl animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Mobile-first responsive layout */}
      <div className="hidden lg:block">
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={handleSelectSession}
          onDeleteSession={handleDeleteSession}
          onNewChat={handleNewChat}
        />
      </div>

      <div className="flex-1 relative z-10 min-w-0">
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </div>

      {/* Mobile sidebar overlay - implement if needed */}
      {/* TODO: Add mobile sidebar toggle and overlay */}
    </div>
  );
}

export default App;
