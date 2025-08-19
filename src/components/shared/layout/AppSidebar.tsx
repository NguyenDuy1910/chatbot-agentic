import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Home, MessageSquare, Settings, Database, BarChart,
  Users, FileText, Grid, Upload, Crown,
  Plus, Palette, ChevronDown
} from 'lucide-react';
import {
  Button,
  Divider,
  Listbox,
  ListboxItem,
} from '@heroui/react';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
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
    path: '/chat'
  },
  {
    id: 'notebooks',
    label: 'Notebooks',
    icon: <Grid className="h-4 w-4" />,
    path: '/notebooks'
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
    path: '/connections'
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

// Additional menu items for testing scroll
const additionalItems = [
  {
    id: 'reports',
    label: 'Reports',
    icon: <FileText className="h-4 w-4" />,
    path: '/reports'
  },
  {
    id: 'integrations',
    label: 'Integrations',
    icon: <Grid className="h-4 w-4" />,
    path: '/integrations'
  },
  {
    id: 'api-keys',
    label: 'API Keys',
    icon: <Database className="h-4 w-4" />,
    path: '/api-keys'
  },
  {
    id: 'billing',
    label: 'Billing',
    icon: <Palette className="h-4 w-4" />,
    path: '/billing'
  },
  {
    id: 'security',
    label: 'Security',
    icon: <Settings className="h-4 w-4" />,
    path: '/security'
  },
  {
    id: 'logs',
    label: 'System Logs',
    icon: <FileText className="h-4 w-4" />,
    path: '/logs'
  }
];

export const AppSidebar: React.FC<AppSidebarProps> = ({
  currentPage = 'main',
  isCollapsed = false,
  onNavigate,
  user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    role: 'admin'
  }
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showScrollIndicator, setShowScrollIndicator] = useState(false);

  useEffect(() => {
    const checkScrollable = () => {
      if (scrollRef.current) {
        const { scrollHeight, clientHeight } = scrollRef.current;
        setShowScrollIndicator(scrollHeight > clientHeight);
      }
    };

    checkScrollable();
    window.addEventListener('resize', checkScrollable);
    return () => window.removeEventListener('resize', checkScrollable);
  }, []);

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
      'admin': '/admin',
      'docs': '/docs',
      'community': '/community',
      'analytics': '/analytics',
      'reports': '/reports'
    };

    const itemPath = pathMap[itemId];
    if (!itemPath) return false;

    // Check exact match or starts with path
    const isMatch = location.pathname === itemPath ||
                   (itemPath !== '/' && location.pathname.startsWith(itemPath + '/'));

    return isMatch;
  };

  const filteredMenuItems = menuItems.filter(item =>
    !item.adminOnly || (item.adminOnly && user?.role === 'admin')
  );

  if (isCollapsed) {
    return (
      <div className="w-16 h-full bg-background border-r border-divider flex flex-col">
        {/* Collapsed Menu */}
        <div className="flex-1 p-2 space-y-2 overflow-y-auto scroll-smooth">
          <Button
            isIconOnly
            color="primary"
            variant="flat"
            size="sm"
            className="w-full"
          >
            <Plus className="h-4 w-4" />
          </Button>

          {filteredMenuItems.map((item) => (
            <div key={item.id} className="relative">
              <Button
                isIconOnly
                variant={isActive(item.id) ? "flat" : "light"}
                color={isActive(item.id) ? "primary" : "default"}
                size="sm"
                className={`w-full transition-all duration-200 ${isActive(item.id) ? 'bg-blue-100 border-blue-300' : ''}`}
                onPress={() => handleNavigate(item.path)}
              >
                {item.icon}
              </Button>

            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-64 h-full bg-background border-r border-divider flex flex-col">
      {/* Navigation Menu */}
      <div
        ref={scrollRef}
        className="flex-1 p-4 space-y-4 overflow-y-auto scroll-smooth relative"
      >
        <Button
          color="primary"
          variant="flat"
          startContent={<Plus className="h-4 w-4" />}
          className="w-full justify-start"
        >
          New
        </Button>

        <div>
          <h3 className="text-xs font-medium text-default-500 mb-3 uppercase tracking-wider">
            Workspace
          </h3>
          <Listbox
            aria-label="Workspace navigation"
            variant="flat"
            selectionMode="none"
          >
            {filteredMenuItems.map((item) => (
              <ListboxItem
                key={item.id}
                startContent={item.icon}
                onPress={() => handleNavigate(item.path)}
                className={`mb-1 transition-all duration-200 ${isActive(item.id) ? 'bg-blue-50 text-blue-600 font-semibold border-r-2 border-blue-500' : 'hover:bg-gray-50'}`}
              >
                {item.label}
              </ListboxItem>
            ))}
          </Listbox>
        </div>

        <Divider />

        <div>
          <h3 className="text-xs font-medium text-default-500 mb-3 uppercase tracking-wider">
            Resources
          </h3>
          <Listbox
            aria-label="Resources navigation"
            variant="flat"
            selectionMode="none"
          >
            {resourceItems.map((item) => (
              <ListboxItem
                key={item.id}
                startContent={item.icon}
                onPress={() => handleNavigate(item.path)}
                className={`mb-1 transition-all duration-200 ${isActive(item.id) ? 'bg-blue-50 text-blue-600 font-semibold border-r-2 border-blue-500' : 'hover:bg-gray-50'}`}
              >
                {item.label}
              </ListboxItem>
            ))}
          </Listbox>
        </div>

        <Divider />

        <div>
          <h3 className="text-xs font-medium text-default-500 mb-3 uppercase tracking-wider">
            Tools & Settings
          </h3>
          <Listbox
            aria-label="Tools navigation"
            variant="flat"
            selectionMode="none"
          >
            {additionalItems.map((item) => (
              <ListboxItem
                key={item.id}
                startContent={item.icon}
                onPress={() => handleNavigate(item.path)}
                className={`mb-1 transition-all duration-200 ${isActive(item.id) ? 'bg-blue-50 text-blue-600 font-semibold border-r-2 border-blue-500' : 'hover:bg-gray-50'}`}
              >
                {item.label}
              </ListboxItem>
            ))}
          </Listbox>
        </div>

        {/* Scroll Indicator */}
        {showScrollIndicator && (
          <div className="absolute bottom-2 right-2 opacity-50 animate-bounce">
            <ChevronDown className="h-4 w-4 text-default-400" />
          </div>
        )}
      </div>


    </div>
  );
};

export default AppSidebar;
