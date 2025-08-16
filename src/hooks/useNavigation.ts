import { useState, useEffect } from 'react';
import {
  getCurrentPath,
  getCurrentPageFromPath,
  generateBreadcrumbs,
  setupNavigationListeners,
  navigateToPath
} from '@/lib/navigation';

export interface NavigationState {
  currentPage: string;
  previousPage: string | null;
  breadcrumbs: string[];
}

export const useNavigation = () => {
  const [navigationState, setNavigationState] = useState<NavigationState>({
    currentPage: getCurrentPageFromPath(getCurrentPath()),
    previousPage: null,
    breadcrumbs: generateBreadcrumbs(getCurrentPath())
  });

  // Update navigation state when URL changes
  useEffect(() => {
    const updateNavigationState = (path: string) => {
      const newPage = getCurrentPageFromPath(path);

      setNavigationState(prev => ({
        currentPage: newPage,
        previousPage: prev.currentPage !== newPage ? prev.currentPage : prev.previousPage,
        breadcrumbs: generateBreadcrumbs(path)
      }));
    };

    // Setup navigation listeners using utility
    const cleanup = setupNavigationListeners(updateNavigationState);

    return cleanup;
  }, []);

  // Navigate to a new page using utility
  const navigateTo = (path: string) => {
    navigateToPath(path);
  };

  // Go back to previous page
  const goBack = () => {
    window.history.back();
  };

  // Check if a page is active
  const isPageActive = (pageId: string): boolean => {
    return navigationState.currentPage === pageId;
  };

  // Get page title
  const getPageTitle = (pageId?: string): string => {
    const page = pageId || navigationState.currentPage;
    const titles: { [key: string]: string } = {
      'main': 'What do you want to analyze today?',
      'chat': 'Chat with Vikki',
      'admin': 'Admin Dashboard',
      'connections': 'Data Connections',
      'notebooks': 'Notebooks',
      'files': 'Files',
      'settings': 'Settings',
      'demo': 'UI Demo',
      'docs': 'Documentation',
      'community': 'Community',
      'analytics': 'Analytics'
    };

    return titles[page] || 'Vikki ChatBot';
  };

  // Get page subtitle
  const getPageSubtitle = (pageId?: string): string => {
    const page = pageId || navigationState.currentPage;
    const subtitles: { [key: string]: string } = {
      'main': 'Your AI-powered data analysis platform',
      'chat': 'Your intelligent assistant is ready to help',
      'admin': 'System administration and management',
      'connections': 'Manage your data sources and integrations',
      'notebooks': 'Create and manage analysis notebooks',
      'files': 'Upload and manage your files',
      'settings': 'Configure your preferences',
      'demo': 'Explore UI components and design system',
      'docs': 'Learn how to use Vikki ChatBot',
      'community': 'Connect with other users',
      'analytics': 'View usage analytics and insights'
    };

    return subtitles[page] || 'AI-powered chatbot for your business';
  };

  return {
    navigationState,
    navigateTo,
    goBack,
    isPageActive,
    getPageTitle,
    getPageSubtitle
  };
};
