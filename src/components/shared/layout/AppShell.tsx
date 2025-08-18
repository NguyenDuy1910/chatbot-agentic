import React, { useState, useEffect } from 'react';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import { AppFooter } from './AppFooter';
import { MainContentRouter } from './MainContentRouter';
import { useNavigation } from '@/hooks/useNavigation';
import '@/styles/components/julius-ai-styles.css';

interface AppShellProps {
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  showFooter?: boolean;
  showExtendedFooter?: boolean;
  onUserMenuClick?: () => void;
}

/**
 * App Shell - Static layout with header, sidebar, footer
 * Only the main content area changes when navigating
 */
export const AppShell: React.FC<AppShellProps> = ({
  user,
  showFooter = true,
  showExtendedFooter = false,
  onUserMenuClick
}) => {
  const { navigationState } = useNavigation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1024; // lg breakpoint
      setIsMobile(mobile);
      
      if (mobile) {
        setSidebarCollapsed(false);
        setSidebarOpen(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleMenuToggle = () => {
    if (isMobile) {
      setSidebarOpen(!sidebarOpen);
    } else {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };



  return (
    <div className="julius-app-layout">
      {/* Static Header */}
      <AppHeader
        currentPage={navigationState.currentPage}
        onMenuToggle={handleMenuToggle}
        user={user}
        onUserMenuClick={onUserMenuClick}
      />

      {/* Main Container */}
      <div className="julius-main-container">
        {/* Mobile Sidebar Overlay */}
        {isMobile && sidebarOpen && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <div 
              className="fixed inset-0 bg-black/50" 
              onClick={() => setSidebarOpen(false)} 
            />
            <div className="fixed inset-y-0 left-0 z-50">
              <AppSidebar
                isCollapsed={false}
                user={user}
              />
            </div>
          </div>
        )}

        {/* Static Desktop Sidebar */}
        <div className={`hidden lg:block ${sidebarCollapsed ? 'w-16' : 'w-64'} transition-all duration-300`}>
          <AppSidebar
            isCollapsed={sidebarCollapsed}
            user={user}
          />
        </div>

        {/* Dynamic Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <main className="flex-1 overflow-auto bg-gray-50">
            <MainContentRouter />
          </main>
        </div>
      </div>

      {/* Static Footer */}
      {showFooter && (
        <AppFooter 
          showExtended={showExtendedFooter}
          companyName="Vikki ChatBot"
          version="1.0.0"
        />
      )}
    </div>
  );
};

export default AppShell;
