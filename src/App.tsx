import { useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { ChatArea } from '@/components/ChatArea';
import { useChat } from '@/hooks/useChat';

function App() {
  const {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    handleNewChat,
    handleSelectSession,
    handleDeleteSession,
    handleSendMessage,
    stop,
  } = useChat({
    onError: (error) => {
      console.error('Chat error:', error);
      // You can add toast notifications here
    },
  });

  // Initialize with a default session if none exist
  useEffect(() => {
    if (sessions.length === 0) {
      handleNewChat();
    }
  }, [sessions.length, handleNewChat]);

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
          onStop={stop}
        />
      </div>

      {/* Mobile sidebar overlay - implement if needed */}
      {/* TODO: Add mobile sidebar toggle and overlay */}
    </div>
  );
}

export default App;
