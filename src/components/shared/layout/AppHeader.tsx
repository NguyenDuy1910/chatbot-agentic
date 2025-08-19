import React from 'react';
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Button,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Avatar,
  Badge,
  Chip,
} from '@heroui/react';
import { Menu, Bell, Settings, User, Crown, Sparkles, LogOut, Sun, Moon } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

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
  user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    role: 'admin'
  },
  onUserMenuClick
}) => {
  const { theme, setTheme, actualTheme } = useTheme();
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
    <Navbar
      maxWidth="full"
      className="bg-white/80 backdrop-blur-md border-b border-divider"
      height="4rem"
    >
      {/* Left Section */}
      <NavbarContent justify="start">
        {/* Mobile Menu Button */}
        <NavbarItem className="lg:hidden">
          <Button
            isIconOnly
            variant="light"
            onPress={onMenuToggle}
            className="text-default-500"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </NavbarItem>

        {/* Logo & Branding */}
        <NavbarBrand className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <div className="hidden sm:flex flex-col">
            <h1 className="text-lg font-bold text-foreground">
              {getPageTitle()}
            </h1>
            <p className="text-sm text-default-500 hidden md:block">
              {getPageSubtitle()}
            </p>
          </div>
        </NavbarBrand>
      </NavbarContent>

      {/* Right Section */}
      <NavbarContent justify="end">
        {/* Notifications */}
        <NavbarItem>
          <Badge content="3" color="danger" size="sm">
            <Button
              isIconOnly
              variant="light"
              className="text-default-500"
            >
              <Bell className="h-5 w-5" />
            </Button>
          </Badge>
        </NavbarItem>

        {/* Theme Toggle */}
        <NavbarItem>
          <Button
            isIconOnly
            variant="light"
            className="text-default-500"
            onPress={() => setTheme(actualTheme === 'dark' ? 'light' : 'dark')}
          >
            {actualTheme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>
        </NavbarItem>

        {/* Settings */}
        <NavbarItem>
          <Button
            isIconOnly
            variant="light"
            className="text-default-500"
          >
            <Settings className="h-5 w-5" />
          </Button>
        </NavbarItem>

        {/* User Menu */}
        <NavbarItem>
          <Dropdown placement="bottom-end">
            <DropdownTrigger>
              <div className="flex items-center gap-2 cursor-pointer">
                <Avatar
                  src={user?.avatar}
                  name={user?.name}
                  size="sm"
                  className="transition-transform"
                />
                <div className="hidden sm:flex flex-col items-start">
                  <span className="text-sm font-medium text-foreground">
                    {user?.name}
                  </span>
                  {user?.role === 'admin' && (
                    <Chip
                      size="sm"
                      variant="flat"
                      color="warning"
                      startContent={<Crown className="h-3 w-3" />}
                      className="h-5"
                    >
                      Admin
                    </Chip>
                  )}
                </div>
              </div>
            </DropdownTrigger>
            <DropdownMenu aria-label="User menu actions">
              <DropdownItem
                key="profile"
                className="h-14 gap-2"
                textValue="Profile"
              >
                <div className="flex flex-col">
                  <span className="font-medium">{user?.name}</span>
                  <span className="text-sm text-default-500">{user?.email}</span>
                </div>
              </DropdownItem>
              <DropdownItem
                key="settings"
                startContent={<User className="h-4 w-4" />}
                onPress={onUserMenuClick}
              >
                Profile
              </DropdownItem>
              <DropdownItem
                key="preferences"
                startContent={<Settings className="h-4 w-4" />}
              >
                Settings
              </DropdownItem>
              <DropdownItem
                key="logout"
                color="danger"
                startContent={<LogOut className="h-4 w-4" />}
              >
                Sign out
              </DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
};

export default AppHeader;
