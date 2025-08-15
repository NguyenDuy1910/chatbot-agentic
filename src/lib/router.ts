import React from 'react';

// URL Router utility for admin management pages
export interface RouteParams {
  [key: string]: string | undefined;
}

export interface AdminRoute {
  path: string;
  title: string;
  description: string;
  component: string;
}

// Admin management routes configuration
export const adminRoutes: Record<string, AdminRoute> = {
  overview: {
    path: '/admin',
    title: 'Dashboard Overview',
    description: 'Main dashboard with statistics and recent activity',
    component: 'DashboardOverview'
  },
  users: {
    path: '/admin/users',
    title: 'User Management',
    description: 'Manage user accounts, roles, and permissions',
    component: 'UserManagement'
  },
  chats: {
    path: '/admin/chats',
    title: 'Chat Analytics',
    description: 'View chat statistics and conversation analytics',
    component: 'ChatVisualization'
  },
  prompts: {
    path: '/admin/prompts',
    title: 'Prompt Management',
    description: 'Create, edit, and manage AI prompts and templates',
    component: 'AdminPromptManagement'
  },
  settings: {
    path: '/admin/settings',
    title: 'System Settings',
    description: 'Configure system parameters and security settings',
    component: 'SystemSettings'
  },
  uris: {
    path: '/admin/uris',
    title: 'URI Management',
    description: 'View and manage all admin page URLs and navigation',
    component: 'ManagementUriPage'
  }
};

// URL management utilities
export class AdminRouter {
  
  // Get current admin route from URL
  static getCurrentRoute(): string {
    const path = window.location.pathname;
    
    if (path === '/admin') return 'overview';
    if (path.startsWith('/admin/users')) return 'users';
    if (path.startsWith('/admin/chats')) return 'chats';
    if (path.startsWith('/admin/prompts')) return 'prompts';
    if (path.startsWith('/admin/settings')) return 'settings';
    if (path.startsWith('/admin/uris')) return 'uris';
    
    return 'overview'; // default
  }
  
  // Navigate to admin route
  static navigateTo(route: string, params?: RouteParams): void {
    const routeConfig = adminRoutes[route];
    if (!routeConfig) {
      console.error(`Route "${route}" not found`);
      return;
    }
    
    let url = routeConfig.path;
    
    // Add query parameters if provided
    if (params && Object.keys(params).length > 0) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.set(key, value);
        }
      });
      url += `?${searchParams.toString()}`;
    }
    
    // Update URL without page reload
    window.history.pushState({}, '', url);
    
    // Trigger route change event
    window.dispatchEvent(new PopStateEvent('popstate'));
  }
  
  // Get query parameters from current URL
  static getQueryParams(): RouteParams {
    const params: RouteParams = {};
    const searchParams = new URLSearchParams(window.location.search);
    
    searchParams.forEach((value, key) => {
      params[key] = value;
    });
    
    return params;
  }
  
  // Build URL for admin route
  static buildUrl(route: string, params?: RouteParams): string {
    const routeConfig = adminRoutes[route];
    if (!routeConfig) return '/admin';
    
    let url = routeConfig.path;
    
    if (params && Object.keys(params).length > 0) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.set(key, value);
        }
      });
      url += `?${searchParams.toString()}`;
    }
    
    return url;
  }
  
  // Get route configuration
  static getRouteConfig(route: string): AdminRoute | undefined {
    return adminRoutes[route];
  }
  
  // Get all available routes
  static getAllRoutes(): AdminRoute[] {
    return Object.values(adminRoutes);
  }
  
  // Check if current URL is an admin route
  static isAdminRoute(): boolean {
    return window.location.pathname.startsWith('/admin');
  }
  
  // Generate breadcrumbs for current route
  static getBreadcrumbs(): Array<{title: string, path: string}> {
    const currentRoute = this.getCurrentRoute();
    const routeConfig = adminRoutes[currentRoute];
    
    const breadcrumbs = [
      { title: 'Admin', path: '/admin' }
    ];
    
    if (currentRoute !== 'overview' && routeConfig) {
      breadcrumbs.push({
        title: routeConfig.title,
        path: routeConfig.path
      });
    }
    
    return breadcrumbs;
  }
}

// Hook for React components to use routing
export const useAdminRouter = () => {
  const [currentRoute, setCurrentRoute] = React.useState(AdminRouter.getCurrentRoute());
  
  React.useEffect(() => {
    const handleRouteChange = () => {
      setCurrentRoute(AdminRouter.getCurrentRoute());
    };
    
    window.addEventListener('popstate', handleRouteChange);
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
    };
  }, []);
  
  return {
    currentRoute,
    navigateTo: AdminRouter.navigateTo,
    getQueryParams: AdminRouter.getQueryParams,
    buildUrl: AdminRouter.buildUrl,
    getRouteConfig: AdminRouter.getRouteConfig,
    getBreadcrumbs: AdminRouter.getBreadcrumbs
  };
};

export default AdminRouter;
