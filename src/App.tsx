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
    <div className="flex h-screen bg-gradient-to-br from-[#f8fafc] via-[#e0e7ef] to-[#f1f5f9] overflow-hidden relative">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[20%] left-[20%] w-40 lg:w-64 aspect-square bg-primary/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-[30%] right-[20%] w-32 lg:w-48 aspect-square bg-purple-400/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-[45%] right-[35%] w-24 lg:w-32 aspect-square bg-blue-400/10 rounded-full blur-2xl animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Sidebar */}
      <aside className="hidden lg:block h-full z-10 p-4">
        <div className="h-full bg-white/80 backdrop-blur-md shadow-xl border-r border-border/30 rounded-3xl flex flex-col transition-all duration-300">
          <Sidebar
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelectSession={handleSelectSession}
            onDeleteSession={handleDeleteSession}
            onNewChat={handleNewChat}
          />
        </div>
      </aside>

      {/* Main chat area */}
      <main className="flex-1 relative z-10 min-w-0 p-4">
        <div className="w-full h-full bg-white/70 backdrop-blur-lg rounded-3xl shadow-2xl border border-border/20 flex flex-col overflow-hidden transition-all duration-300">
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onStop={stop}
          />
        </div>
      </main>

      {/* Mobile sidebar overlay - implement if needed */}
      {/* TODO: Add mobile sidebar toggle and overlay */}
    </div>
  );
}

export default App;
