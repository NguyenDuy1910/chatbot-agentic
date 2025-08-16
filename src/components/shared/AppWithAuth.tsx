import React, { useState } from 'react';
import { AuthProvider, useAuth, LoginForm, UserProfileComponent, UserMenu } from '@/components/features/auth';
import { ChatInput, ChatArea } from '@/components/features/chat';
import { AdminDashboard } from '@/components/features/admin/AdminDashboard';
import { LoadingState } from '@/components/features/admin/DashboardStates';
import { Button } from '@/components/shared/ui/Button';
import { Crown, MessageSquare, User as UserIcon, Menu, X } from 'lucide-react';
import { Message } from '@/types/features/chat';

const MainApp: React.FC = () => {
  const { isAuthenticated, user, loading, error, login, register, updateProfile, updatePassword } = useAuth();
  const [currentView, setCurrentView] = useState<'chat' | 'profile' | 'admin'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  // Handle sending messages
  const handleSendMessage = (content: string, attachments?: any[]) => {
    if (!user) return;

    const newMessage: Message = {
      id: Math.random().toString(36).substring(2, 11),
      content,
      role: 'user',
      timestamp: new Date(),
      attachments
    };

    setMessages(prev => [...prev, newMessage]);
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: Math.random().toString(36).substring(2, 11),
        content: `Hi ${user.name}! I received your message: "${content}". How can I help you today?`,
        role: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000);
  };

  // Loading state
  if (loading) {
    return <LoadingState message="Initializing Vikki ChatBot..." />;
  }

  // Not authenticated - show login
  if (!isAuthenticated || !user) {
    return (
      <LoginForm
        onLogin={login}
        onRegister={register}
        loading={loading}
        error={error}
      />
    );
  }

  // Authenticated - show main app
  return (
    <div className="flex h-screen bg-background">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-64 bg-background border-r">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="font-semibold">Navigation</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4 space-y-2">
              <Button
                variant={currentView === 'chat' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('chat');
                  setSidebarOpen(false);
                }}
                className="w-full justify-start"
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Chat
              </Button>
              <Button
                variant={currentView === 'profile' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('profile');
                  setSidebarOpen(false);
                }}
                className="w-full justify-start"
              >
                <UserIcon className="h-4 w-4 mr-2" />
                Profile
              </Button>
              {user.role === 'admin' && (
                <Button
                  variant={currentView === 'admin' ? 'default' : 'ghost'}
                  onClick={() => {
                    setCurrentView('admin');
                    setSidebarOpen(false);
                  }}
                  className="w-full justify-start"
                >
                  <Crown className="h-4 w-4 mr-2" />
                  Admin
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:flex-col lg:w-64 lg:border-r lg:bg-muted/30">
        <div className="p-4 border-b">
          <div className="flex items-center gap-2">
            <Crown className="h-6 w-6 text-primary" />
            <h1 className="font-bold text-lg">Vikki ChatBot</h1>
          </div>
        </div>
        <div className="flex-1 p-4 space-y-2">
          <Button
            variant={currentView === 'chat' ? 'default' : 'ghost'}
            onClick={() => setCurrentView('chat')}
            className="w-full justify-start"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Chat
          </Button>
          <Button
            variant={currentView === 'profile' ? 'default' : 'ghost'}
            onClick={() => setCurrentView('profile')}
            className="w-full justify-start"
          >
            <UserIcon className="h-4 w-4 mr-2" />
            Profile
          </Button>
          {user.role === 'admin' && (
            <Button
              variant={currentView === 'admin' ? 'default' : 'ghost'}
              onClick={() => setCurrentView('admin')}
              className="w-full justify-start"
            >
              <Crown className="h-4 w-4 mr-2" />
              Admin Dashboard
            </Button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-10">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden"
              >
                <Menu className="h-4 w-4" />
              </Button>
              <div>
                <h2 className="font-semibold">
                  {currentView === 'chat' && 'Chat with Vikki'}
                  {currentView === 'profile' && 'Profile Settings'}
                  {currentView === 'admin' && 'Admin Dashboard'}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {currentView === 'chat' && 'Your AI assistant is ready to help'}
                  {currentView === 'profile' && 'Manage your account settings'}
                  {currentView === 'admin' && 'System administration'}
                </p>
              </div>
            </div>
            <UserMenu
              user={user}
              onProfileClick={() => setCurrentView('profile')}
            />
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          {currentView === 'chat' && (
            <div className="h-full flex flex-col">
              <div className="flex-1 overflow-hidden">
                <ChatArea 
                  messages={messages} 
                  isLoading={isTyping}
                  onSendMessage={handleSendMessage}
                />
              </div>
              <ChatInput
                onSendMessage={handleSendMessage}
                placeholder={`Hi ${user.name}! Ask me anything...`}
              />
            </div>
          )}

          {currentView === 'profile' && (
            <div className="h-full overflow-auto">
              <UserProfileComponent
                user={user}
                onUpdateProfile={updateProfile}
                onUpdatePassword={updatePassword}
                loading={loading}
              />
            </div>
          )}

          {currentView === 'admin' && user.role === 'admin' && (
            <div className="h-full overflow-auto">
              <AdminDashboard />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Main App with Auth Provider
export const AppWithAuth: React.FC = () => {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
};
