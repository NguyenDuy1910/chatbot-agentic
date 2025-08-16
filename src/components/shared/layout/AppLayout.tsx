import React, { useState, useEffect } from 'react';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import { AppFooter } from './AppFooter';
import { useNavigation } from '@/hooks/useNavigation';
import '@/styles/components/julius-ai-styles.css';

interface AppLayoutProps {
  children: React.ReactNode;
  currentPage?: string;
  showFooter?: boolean;
  showExtendedFooter?: boolean;
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  onNavigate?: (path: string) => void;
  onUserMenuClick?: () => void;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  currentPage,
  showFooter = true,
  showExtendedFooter = false,
  user,
  onNavigate,
  onUserMenuClick
}) => {
  const { navigationState, navigateTo } = useNavigation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Use navigation state if currentPage is not provided
  const activePage = currentPage || navigationState.currentPage;

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

  const handleNavigate = (path: string) => {
    // Close mobile sidebar on navigation
    if (isMobile) {
      setSidebarOpen(false);
    }

    if (onNavigate) {
      onNavigate(path);
    } else {
      navigateTo(path);
    }
  };

  return (
    <div className="julius-app-layout">
      {/* Header */}
      <AppHeader
        currentPage={activePage}
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
                currentPage={activePage}
                isCollapsed={false}
                onNavigate={handleNavigate}
                user={user}
              />
            </div>
          </div>
        )}

        {/* Desktop Sidebar */}
        <div className={`hidden lg:block ${sidebarCollapsed ? 'w-16' : 'w-64'} transition-all duration-300`}>
          <AppSidebar
            currentPage={activePage}
            isCollapsed={sidebarCollapsed}
            onNavigate={handleNavigate}
            user={user}
          />
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <main className="flex-1 overflow-auto bg-gray-50">
            {children}
          </main>
        </div>
      </div>

      {/* Footer */}
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

export default AppLayout;
