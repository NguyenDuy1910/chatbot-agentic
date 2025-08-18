import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Home, MessageSquare, Settings, Database, BarChart,
  Users, FileText, Grid, Upload, Crown, Sparkles,
  ChevronRight, Plus, Palette
} from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';
import '@/styles/components/julius-ai-styles.css';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  count?: number;
  adminOnly?: boolean;
  children?: MenuItem[];
}

interface AppSidebarProps {
  currentPage?: string;
  isCollapsed?: boolean;
  onNavigate?: (path: string) => void;
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
}

const menuItems: MenuItem[] = [
  {
    id: 'main',
    label: 'Home',
    icon: <Home className="h-4 w-4" />,
    path: '/'
  },
  {
    id: 'chat',
    label: 'Chat Threads',
    icon: <MessageSquare className="h-4 w-4" />,
    path: '/chat',
    count: 2
  },
  {
    id: 'notebooks',
    label: 'Notebooks',
    icon: <Grid className="h-4 w-4" />,
    path: '/notebooks',
    count: 4
  },
  {
    id: 'files',
    label: 'Files',
    icon: <Upload className="h-4 w-4" />,
    path: '/files'
  },
  {
    id: 'connections',
    label: 'Data Connectors',
    icon: <Database className="h-4 w-4" />,
    path: '/connections',
    count: 5
  },
  {
    id: 'demo',
    label: 'UI Demo',
    icon: <Palette className="h-4 w-4" />,
    path: '/demo'
  },
  {
    id: 'admin',
    label: 'Admin Dashboard',
    icon: <Crown className="h-4 w-4" />,
    path: '/admin',
    adminOnly: true
  }
];

const resourceItems: MenuItem[] = [
  {
    id: 'docs',
    label: 'Documentation',
    icon: <FileText className="h-4 w-4" />,
    path: '/docs'
  },
  {
    id: 'community',
    label: 'Community',
    icon: <Users className="h-4 w-4" />,
    path: '/community'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: <BarChart className="h-4 w-4" />,
    path: '/analytics'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings className="h-4 w-4" />,
    path: '/settings'
  }
];

export const AppSidebar: React.FC<AppSidebarProps> = ({
  currentPage = 'main',
  isCollapsed = false,
  onNavigate,
  user
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigate = (path: string) => {
    if (onNavigate) {
      onNavigate(path);
    } else {
      navigate(path);
    }
  };

  const isActive = (itemId: string) => {
    // Map item IDs to paths for comparison
    const pathMap: { [key: string]: string } = {
      'main': '/',
      'chat': '/chat',
      'connections': '/connections',
      'notebooks': '/notebooks',
      'files': '/files',
      'settings': '/settings',
      'demo': '/demo',
      'admin': '/admin'
    };

    // Use currentPage prop if provided, otherwise use location
    if (currentPage) {
      return itemId === currentPage;
    }

    const itemPath = pathMap[itemId];
    return location.pathname === itemPath || location.pathname.startsWith(itemPath + '/');
  };

  const filteredMenuItems = menuItems.filter(item => 
    !item.adminOnly || (item.adminOnly && user?.role === 'admin')
  );

  if (isCollapsed) {
    return (
      <div className="julius-sidebar julius-sidebar-collapsed">
        <div className="julius-sidebar-header">
          <div className="julius-logo">
            <Sparkles className="h-4 w-4" />
          </div>
        </div>
        
        <div className="julius-nav-menu">
          <div className="px-2 py-2">
            <Button size="sm" className="w-full p-2">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="space-y-1 px-2">
            {filteredMenuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavigate(item.path)}
                className={`julius-nav-item-collapsed ${isActive(item.id) ? 'active' : ''}`}
                title={item.label}
              >
                {item.icon}
                {item.count && (
                  <span className="julius-nav-count-collapsed">{item.count}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="julius-sidebar">
      {/* Sidebar Header */}
      <div className="julius-sidebar-header">
        <div className="flex items-center space-x-3">
          <div className="julius-logo">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900 text-sm">Vikki ChatBot</h2>
          </div>
        </div>
        <div className="flex items-center space-x-2 mt-3">
          <div className="flex items-center space-x-1 text-xs text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Connected</span>
          </div>
          <div className="flex items-center space-x-1 text-xs text-blue-600">
            <Sparkles className="h-3 w-3" />
            <span>AI</span>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <div className="julius-nav-menu">
        <div className="px-3 py-2">
          <Button className="julius-btn julius-btn-primary w-full">
            <Plus className="h-4 w-4 mr-2" />
            New
          </Button>
        </div>

        <div className="px-3 py-2">
          <div className="text-xs font-medium text-gray-500 mb-2">Workspace</div>
          <div className="space-y-1">
            {filteredMenuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavigate(item.path)}
                className={`julius-nav-item ${isActive(item.id) ? 'active' : ''}`}
              >
                {item.icon}
                <span className="ml-3">{item.label}</span>
                {item.count && (
                  <span className="ml-auto text-xs text-gray-500">{item.count}</span>
                )}
                <ChevronRight className="julius-nav-arrow" />
              </button>
            ))}
          </div>
        </div>

        <div className="px-3 py-2">
          <div className="text-xs font-medium text-gray-500 mb-2">Resources</div>
          <div className="space-y-1">
            {resourceItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavigate(item.path)}
                className="julius-nav-item"
              >
                {item.icon}
                <span className="ml-3">{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="julius-sidebar-footer">
        <div className="flex items-center space-x-3">
          {user?.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="w-8 h-8 rounded-full"
            />
          ) : (
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
              {user?.name?.charAt(0) || 'U'}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-gray-900 truncate">
              {user?.name || 'User'}
            </div>
            <div className="text-xs text-gray-500 truncate">
              {user?.email || 'user@example.com'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppSidebar;
