import React from 'react';
import {
  Navbar,
  Button,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Avatar,
  Badge,
  Chip,
} from '@heroui/react';
import { Menu, Bell, Settings, User, Crown, LogOut, Sun, Moon } from 'lucide-react';
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
  const { setTheme, actualTheme } = useTheme();

  const getPageTitle = () => {
    switch (currentPage) {
      case 'main':
        return 'Home';
      case 'chat':
        return 'Chat';
      case 'admin':
        return 'Admin';
      case 'connections':
        return 'Connections';
      case 'notebooks':
        return 'Notebooks';
      case 'files':
        return 'Files';
      case 'settings':
        return 'Settings';
      case 'demo':
        return 'Demo';
      default:
        return 'Vikki ChatBot';
    }
  };

  return (
    <Navbar
      maxWidth="full"
      className="bg-white/80 backdrop-blur-sm border-b border-default-200/50"
      height="4rem"
    >
      <div className="flex w-full">
        {/* Left Section - Fixed width like sidebar */}
        <div className="w-64 flex items-center px-4">
          {/* Mobile Menu Button */}
          <div className="lg:hidden mr-2">
            <Button
              isIconOnly
              variant="light"
              onPress={onMenuToggle}
              className="text-default-500"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </div>

          {/* Page Title - Simple */}
          <h1 className="text-lg font-semibold text-foreground truncate">
            {getPageTitle()}
          </h1>
        </div>

        {/* Right Section - Flexible content */}
        <div className="flex-1 flex items-center justify-end px-6 gap-2">
          {/* Theme Toggle */}
          <Button
            isIconOnly
            variant="light"
            className="text-default-500 hover:text-primary transition-colors duration-200"
            onPress={() => setTheme(actualTheme === 'dark' ? 'light' : 'dark')}
          >
            {actualTheme === 'dark' ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>

          {/* Notifications */}
          <Badge content="3" color="danger" size="sm">
            <Button
              isIconOnly
              variant="light"
              className="text-default-500 hover:text-primary transition-colors duration-200"
            >
              <Bell className="h-4 w-4" />
            </Button>
          </Badge>

          {/* User Menu - Simplified */}
          <Dropdown placement="bottom-end">
            <DropdownTrigger>
              <div className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity duration-200">
                <Avatar
                  src={user?.avatar}
                  name={user?.name}
                  size="sm"
                  className="transition-transform"
                />
                <span className="text-sm font-medium text-foreground hidden sm:block">
                  {user?.name}
                </span>
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
                  {user?.role === 'admin' && (
                    <Chip
                      size="sm"
                      variant="flat"
                      color="warning"
                      startContent={<Crown className="h-3 w-3" />}
                      className="h-5 mt-1"
                    >
                      Admin
                    </Chip>
                  )}
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
        </div>
      </div>
    </Navbar>
  );
};

export default AppHeader;
