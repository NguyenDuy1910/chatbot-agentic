/**
 * Navigation utilities for SPA routing
 */

export interface NavigationOptions {
  replace?: boolean;
  state?: any;
  showLoading?: boolean;
  loadingText?: string;
  loadingDuration?: number;
}

/**
 * Navigate to a new path in the SPA
 * @param path - The path to navigate to
 * @param options - Navigation options
 */
export const navigateToPath = (path: string, options: NavigationOptions = {}) => {
  const {
    replace = false,
    state = {},
    showLoading = true,
    loadingText = 'Loading...',
    loadingDuration = 800
  } = options;

  // Trigger loading start event if enabled
  if (showLoading) {
    window.dispatchEvent(new CustomEvent('navigation-loading-start', {
      detail: { loadingText, loadingDuration }
    }));
  }

  // Small delay to show loading animation
  setTimeout(() => {
    if (replace) {
      window.history.replaceState(state, '', path);
    } else {
      window.history.pushState(state, '', path);
    }

    // Trigger custom navigation event for router
    window.dispatchEvent(new CustomEvent('navigate', {
      detail: { path, replace, state, showLoading, loadingText }
    }));
  }, showLoading ? 100 : 0);
};

/**
 * Go back in history
 */
export const goBack = () => {
  window.history.back();
};

/**
 * Go forward in history
 */
export const goForward = () => {
  window.history.forward();
};

/**
 * Get current path
 */
export const getCurrentPath = (): string => {
  return window.location.pathname;
};

/**
 * Get current page from path
 */
export const getCurrentPageFromPath = (path: string): string => {
  if (path === '/') return 'main';
  if (path.startsWith('/chat')) return 'chat';
  if (path.startsWith('/admin')) return 'admin';
  if (path.startsWith('/connections')) return 'connections';
  if (path.startsWith('/notebooks')) return 'notebooks';
  if (path.startsWith('/files')) return 'files';
  if (path.startsWith('/settings')) return 'settings';
  if (path.startsWith('/demo')) return 'demo';
  if (path.startsWith('/docs')) return 'docs';
  if (path.startsWith('/community')) return 'community';
  if (path.startsWith('/analytics')) return 'analytics';

  const segments = path.split('/').filter(Boolean);
  return segments[0] || 'main';
};

/**
 * Check if a path is active
 */
export const isPathActive = (currentPath: string, targetPath: string): boolean => {
  if (targetPath === '/') {
    return currentPath === '/';
  }
  return currentPath.startsWith(targetPath);
};

/**
 * Generate breadcrumbs from path
 */
export const generateBreadcrumbs = (path: string): string[] => {
  if (path === '/') return ['Home'];
  
  const segments = path.split('/').filter(Boolean);
  const breadcrumbs = ['Home'];
  
  segments.forEach((segment, index) => {
    const displayName = getPageDisplayName(segment);
    breadcrumbs.push(displayName);
  });
  
  return breadcrumbs;
};

/**
 * Get display name for page segment
 */
export const getPageDisplayName = (segment: string): string => {
  const displayNames: { [key: string]: string } = {
    'chat': 'Chat Threads',
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

  return displayNames[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
};

/**
 * Setup navigation event listeners
 */
export const setupNavigationListeners = (callback: (path: string) => void) => {
  const handlePopState = () => {
    callback(getCurrentPath());
  };

  const handleNavigate = (event: CustomEvent) => {
    callback(event.detail.path);
  };

  // Listen for browser back/forward
  window.addEventListener('popstate', handlePopState);
  
  // Listen for custom navigation events
  window.addEventListener('navigate', handleNavigate as EventListener);

  // Return cleanup function
  return () => {
    window.removeEventListener('popstate', handlePopState);
    window.removeEventListener('navigate', handleNavigate as EventListener);
  };
};
