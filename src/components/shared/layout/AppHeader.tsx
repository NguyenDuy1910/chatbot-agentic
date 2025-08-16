import React, { useState } from 'react';
import { Menu, Bell, Settings, User, Crown, Sparkles } from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';
import '@/styles/components/julius-ai-styles.css';

interface AppHeaderProps {
  currentPage?: string;
  onMenuToggle?: () => void;
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  onUserMenuClick?: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  currentPage = 'Home',
  onMenuToggle,
  user,
  onUserMenuClick
}) => {
  const [showUserMenu, setShowUserMenu] = useState(false);

  const getPageTitle = () => {
    switch (currentPage) {
      case 'main':
        return 'What do you want to analyze today?';
      case 'chat':
        return 'Chat with Vikki';
      case 'admin':
        return 'Admin Dashboard';
      case 'connections':
        return 'Data Connections';
      case 'notebooks':
        return 'Notebooks';
      case 'files':
        return 'Files';
      case 'settings':
        return 'Settings';
      case 'demo':
        return 'UI Demo';
      default:
        return 'Vikki ChatBot';
    }
  };

  const getPageSubtitle = () => {
    switch (currentPage) {
      case 'main':
        return 'Your AI-powered data analysis platform';
      case 'chat':
        return 'Your intelligent assistant is ready to help';
      case 'admin':
        return 'System administration and management';
      case 'connections':
        return 'Manage your data sources and integrations';
      case 'notebooks':
        return 'Create and manage your analysis notebooks';
      case 'files':
        return 'Upload and manage your data files';
      case 'settings':
        return 'Configure your preferences and account';
      case 'demo':
        return 'Explore UI components and design system';
      default:
        return 'AI-powered chatbot for your business';
    }
  };

  return (
    <header className="julius-header">
      <div className="flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center space-x-4">
          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuToggle}
            className="lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* Logo & Branding */}
          <div className="flex items-center space-x-3">
            <div className="julius-logo">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold text-gray-900">
                {getPageTitle()}
              </h1>
              <p className="text-sm text-gray-600 hidden md:block">
                {getPageSubtitle()}
              </p>
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-3">

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs"></span>
          </Button>

          {/* Settings */}
          <Button variant="ghost" size="sm">
            <Settings className="h-5 w-5" />
          </Button>

          {/* User Menu */}
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2"
            >
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="h-6 w-6 rounded-full"
                />
              ) : (
                <div className="h-6 w-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-medium">
                  {user?.name?.charAt(0) || 'U'}
                </div>
              )}
              <span className="hidden sm:block text-sm font-medium">
                {user?.name || 'User'}
              </span>
              {user?.role === 'admin' && (
                <Crown className="h-4 w-4 text-yellow-500" />
              )}
            </Button>

            {/* User Dropdown Menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                <div className="py-1">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                  <button
                    onClick={onUserMenuClick}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                  >
                    <User className="h-4 w-4" />
                    <span>Profile</span>
                  </button>
                  <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2">
                    <Settings className="h-4 w-4" />
                    <span>Settings</span>
                  </button>
                  <div className="border-t border-gray-100">
                    <button className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                      Sign out
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
