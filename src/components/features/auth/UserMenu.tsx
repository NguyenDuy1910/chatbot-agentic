import React, { useState } from 'react';
import { Button } from '@/components/shared/ui/Button';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { 
  User, 
  Settings, 
  LogOut, 
  Shield, 
  ChevronDown,
  Crown,
  MessageSquare
} from 'lucide-react';
import { UserProfile } from '@/types/features/auth';
import { useAuth } from '@/contexts/AuthContext';

interface UserMenuProps {
  user: UserProfile;
  onProfileClick: () => void;
  className?: string;
}

export const UserMenu: React.FC<UserMenuProps> = ({
  user,
  onProfileClick,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* User Avatar Button */}
      <Button
        variant="ghost"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 h-10 px-3 hover:bg-muted/50 transition-colors"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-primary-foreground text-sm font-medium overflow-hidden">
          {user.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="w-full h-full object-cover"
            />
          ) : (
            user.name.charAt(0).toUpperCase()
          )}
        </div>
        <span className="font-medium text-sm hidden sm:inline">{user.name}</span>
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Menu */}
          <Card className="absolute top-full right-0 mt-2 w-72 z-20 shadow-xl border-0 bg-background/95 backdrop-blur-sm">
            <CardContent className="p-0">
              {/* User Info Header */}
              <div className="p-4 border-b bg-gradient-to-r from-primary/5 to-primary/10">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-primary-foreground font-medium overflow-hidden">
                    {user.avatar ? (
                      <img
                        src={user.avatar}
                        alt={user.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      user.name.charAt(0).toUpperCase()
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-foreground truncate">{user.name}</div>
                    <div className="text-sm text-muted-foreground truncate">{user.email}</div>
                    <div className="flex items-center gap-2 mt-1">
                      {user.role === 'admin' && (
                        <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/20 text-primary text-xs">
                          <Crown className="h-3 w-3" />
                          Admin
                        </div>
                      )}
                      <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-xs">
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                        {user.status}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="p-4 border-b">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="text-lg font-bold text-primary">{user.totalChats}</div>
                    <div className="text-xs text-muted-foreground">Chats</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold text-green-600">{user.totalMessages}</div>
                    <div className="text-xs text-muted-foreground">Messages</div>
                  </div>
                </div>
              </div>

              {/* Menu Items */}
              <div className="p-2">
                <Button
                  variant="ghost"
                  onClick={() => {
                    onProfileClick();
                    setIsOpen(false);
                  }}
                  className="w-full justify-start h-auto p-3 hover:bg-muted/50"
                >
                  <User className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium">Profile Settings</div>
                    <div className="text-xs text-muted-foreground">Manage your account</div>
                  </div>
                </Button>

                {user.role === 'admin' && (
                  <Button
                    variant="ghost"
                    onClick={() => {
                      // Navigate to admin dashboard
                      setIsOpen(false);
                    }}
                    className="w-full justify-start h-auto p-3 hover:bg-muted/50"
                  >
                    <Shield className="h-4 w-4 mr-3" />
                    <div className="text-left">
                      <div className="font-medium">Admin Dashboard</div>
                      <div className="text-xs text-muted-foreground">Manage system</div>
                    </div>
                  </Button>
                )}

                <Button
                  variant="ghost"
                  onClick={() => {
                    // Navigate to chat history
                    setIsOpen(false);
                  }}
                  className="w-full justify-start h-auto p-3 hover:bg-muted/50"
                >
                  <MessageSquare className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium">Chat History</div>
                    <div className="text-xs text-muted-foreground">View past conversations</div>
                  </div>
                </Button>

                <Button
                  variant="ghost"
                  onClick={() => {
                    // Navigate to settings
                    setIsOpen(false);
                  }}
                  className="w-full justify-start h-auto p-3 hover:bg-muted/50"
                >
                  <Settings className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium">Preferences</div>
                    <div className="text-xs text-muted-foreground">App settings</div>
                  </div>
                </Button>

                <div className="border-t my-2" />

                <Button
                  variant="ghost"
                  onClick={handleLogout}
                  className="w-full justify-start h-auto p-3 hover:bg-destructive/10 hover:text-destructive text-muted-foreground"
                >
                  <LogOut className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium">Sign Out</div>
                    <div className="text-xs opacity-70">Exit your account</div>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};
