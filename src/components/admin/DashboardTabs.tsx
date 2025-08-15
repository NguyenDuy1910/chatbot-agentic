import React from 'react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { BarChart3, Users, Settings, Sparkles, MessageSquare, Link } from 'lucide-react';

interface DashboardTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  children: React.ReactNode;
}

export const DashboardTabs: React.FC<DashboardTabsProps> = ({
  activeTab,
  onTabChange,
  children
}) => {
  const tabs = [
    {
      value: 'overview',
      label: 'Overview',
      icon: <BarChart3 className="h-4 w-4" />
    },
    {
      value: 'users',
      label: 'Users',
      icon: <Users className="h-4 w-4" />
    },
    {
      value: 'chats',
      label: 'Vikki Chats',
      icon: <MessageSquare className="h-4 w-4" />
    },
    {
      value: 'prompts',
      label: 'Prompts',
      icon: <Sparkles className="h-4 w-4" />
    },
    {
      value: 'settings',
      label: 'Settings',
      icon: <Settings className="h-4 w-4" />
    },
    {
      value: 'uris',
      label: 'URI Management',
      icon: <Link className="h-4 w-4" />
    }
  ];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8">
      <Tabs value={activeTab} onValueChange={onTabChange}>
        <div className="mb-6 overflow-x-auto">
          <TabsList className="grid w-full grid-cols-6 lg:w-auto lg:inline-flex min-w-max">
            {tabs.map(tab => (
              <TabsTrigger 
                key={tab.value}
                value={tab.value} 
                className="flex items-center gap-2 whitespace-nowrap px-3 sm:px-4 py-2 text-xs sm:text-sm"
              >
                {tab.icon}
                <span className="hidden sm:inline lg:inline">{tab.label}</span>
                <span className="sm:hidden lg:hidden">
                  {tab.label.split(' ')[0]}
                </span>
              </TabsTrigger>
            ))}
          </TabsList>
        </div>
        
        {children}
      </Tabs>
    </div>
  );
};
