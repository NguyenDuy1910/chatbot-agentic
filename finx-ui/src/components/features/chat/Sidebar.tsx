import React, { useState } from 'react';
import { ChatSession } from '@/types/features/chat';
import { cn } from '@/lib/utils';
import { MessageSquare, Trash2, BookOpen, Database } from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';
import { PromptManager } from '@/components/features/prompts/PromptManager';
import { DatabaseManager } from '@/components/features/database/DatabaseManager';

interface SidebarProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onNewChat: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat
}) => {
  const [activeTab, setActiveTab] = useState<'chats' | 'prompts' | 'database'>('chats');
  return (
    <div className="w-80 max-w-[90vw] lg:max-w-none bg-gradient-to-b from-background to-muted/30 border-r border-border/50 flex flex-col h-full backdrop-blur-sm overflow-x-hidden">
      {/* Header with tabs */}
      <div className="px-4 py-3 border-b border-border/50 bg-gradient-to-r from-background/80 to-muted/20 backdrop-blur-sm shrink-0">
        <div className="flex rounded-xl bg-muted/30 p-1.5 backdrop-blur-sm border border-border/30">
          <button
            onClick={() => setActiveTab('chats')}
            className={cn(
              'flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 min-w-0 whitespace-nowrap overflow-hidden text-ellipsis',
              activeTab === 'chats'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/30 scale-105'
                : 'text-muted-foreground hover:text-foreground hover:bg-background/50 hover:scale-102'
            )}
          >
            <MessageSquare className="h-3 w-3 lg:h-4 lg:w-4" />
            <span className="hidden sm:inline">Chats</span>
          </button>
          <button
            onClick={() => setActiveTab('prompts')}
            className={cn(
              'flex-1 flex items-center justify-center gap-1 lg:gap-2 px-2 lg:px-3 py-2 rounded-lg text-xs lg:text-sm font-medium transition-all duration-300 min-w-0 whitespace-nowrap overflow-hidden text-ellipsis',
              activeTab === 'prompts'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/30 scale-105'
                : 'text-muted-foreground hover:text-foreground hover:bg-background/50 hover:scale-102'
            )}
          >
            <BookOpen className="h-3 w-3 lg:h-4 lg:w-4" />
            <span className="hidden sm:inline">Prompts</span>
          </button>
          <button
            onClick={() => setActiveTab('database')}
            className={cn(
              'flex-1 flex items-center justify-center gap-1 lg:gap-2 px-2 lg:px-3 py-2 rounded-lg text-xs lg:text-sm font-medium transition-all duration-300',
              activeTab === 'database'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/30 scale-105'
                : 'text-muted-foreground hover:text-foreground hover:bg-background/50 hover:scale-102'
            )}
          >
            <Database className="h-3 w-3 lg:h-4 lg:w-4" />
            <span className="hidden sm:inline">Database</span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chats' ? (
          <div className="h-full flex flex-col fade-in overflow-hidden ">
            <div className="px-4 py-3 border-b border-border/30">
              <Button
                onClick={onNewChat}
                className="w-full justify-start gap-2 bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg shadow-primary/20 hover:shadow-primary/30 hover:scale-102 transition-all duration-300 text-sm"
              >
                <MessageSquare className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar px-4 py-2">
              {sessions.length === 0 ? (
                <div className="text-center text-muted-foreground py-8 fade-in">
                  <MessageSquare className="h-10 w-10 mx-auto mb-4 opacity-50 animate-float" />
                  <p className="text-sm">No conversations yet</p>
                  <p className="text-xs mt-2 opacity-70">Start a new chat to get started</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {sessions.map((session, index) => (
                    <div
                      key={session.id}
                      className={cn(
                        'group relative rounded-xl cursor-pointer transition-all duration-300 hover:scale-102 scale-in',
                        currentSessionId === session.id
                          ? 'bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 shadow-lg shadow-primary/10'
                          : 'hover:bg-gradient-to-r hover:from-muted/50 hover:to-muted/30 hover:shadow-md'
                      )}
                      style={{ animationDelay: `${index * 50}ms` }}
                      onClick={() => onSelectSession(session.id)}
                    >
                      <div className="p-3">
                        <div className="flex-1 min-w-0 pr-8">
                          <p className="text-sm font-medium truncate mb-1.5">
                            {session.title}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {session.updatedAt.toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 h-6 w-6 hover:bg-destructive/10 hover:text-destructive transition-all duration-200 hover:scale-110"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteSession(session.id);
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : activeTab === 'prompts' ? (
          <div className="h-full slide-in-right overflow-hidden">
            <PromptManager compact />
          </div>
        ) : (
          <div className="h-full slide-in-left overflow-hidden">
            <DatabaseManager compact />
          </div>
        )}
      </div>
      
      <div className="px-4 py-3 border-t border-border/30 bg-gradient-to-r from-muted/20 to-background/50 backdrop-blur-sm shrink-0">
        <div className="text-xs text-muted-foreground text-center gradient-text font-medium">
          Powered by Vikki ChatBot ✨
        </div>
      </div>
    </div>
  );
};
