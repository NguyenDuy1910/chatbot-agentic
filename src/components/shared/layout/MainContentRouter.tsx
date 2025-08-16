import React, { useState, useEffect } from 'react';
import {
  ChatPage, AdminPage, ConnectionsPage, MainPage,
  NotebooksPage, FilesPage, SettingsPage, DemoPage
} from '@/pages';
import { PageTransition } from '@/components/shared/ui';
import { setupNavigationListeners, getCurrentPath, getCurrentPageFromPath } from '@/lib/navigation';

/**
 * Main Content Router - Only renders the main content area
 * Header, Sidebar, and Footer remain static
 */
export const MainContentRouter: React.FC = () => {
  const [currentPath, setCurrentPath] = useState(getCurrentPath());
  const [isNavigating, setIsNavigating] = useState(false);
  const [loadingText, setLoadingText] = useState('Loading...');

  // Listen for navigation changes
  useEffect(() => {
    const cleanup = setupNavigationListeners((path: string) => {
      setCurrentPath(path);
      // Stop loading after navigation
      setTimeout(() => setIsNavigating(false), 300);
    });

    // Listen for loading events
    const handleLoadingStart = (event: CustomEvent) => {
      setLoadingText(event.detail.loadingText || 'Loading...');
      setIsNavigating(true);
    };

    const handleLoadingStop = () => {
      setIsNavigating(false);
    };

    window.addEventListener('navigation-loading-start', handleLoadingStart as EventListener);
    window.addEventListener('navigation-loading-stop', handleLoadingStop);

    return () => {
      cleanup();
      window.removeEventListener('navigation-loading-start', handleLoadingStart as EventListener);
      window.removeEventListener('navigation-loading-stop', handleLoadingStop);
    };
  }, []);

  // Route matching logic
  const renderMainContent = () => {
    const currentPage = getCurrentPageFromPath(currentPath);

    switch (true) {
      case currentPath.startsWith('/admin'):
        return <AdminPage />;

      case currentPath.startsWith('/connections'):
        return <ConnectionsPage />;

      case currentPath === '/':
        return <MainPage />;

      case currentPath.startsWith('/chat'):
        return <ChatPage />;

      case currentPath.startsWith('/notebooks'):
        return <NotebooksPage />;

      case currentPath.startsWith('/files'):
        return <FilesPage />;

      case currentPath.startsWith('/settings'):
        return <SettingsPage />;

      case currentPath.startsWith('/demo'):
        return <DemoPage />;

      default:
        return (
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-800">404 - Page Not Found</h1>
              <p className="text-gray-600">The page you're looking for doesn't exist.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <PageTransition isLoading={isNavigating} loadingText={loadingText}>
      {renderMainContent()}
    </PageTransition>
  );
};

export default MainContentRouter;
