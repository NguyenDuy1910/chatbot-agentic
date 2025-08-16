import React from 'react';
import { Button } from '@/components/shared/ui';
import { navigateToPath } from '@/lib/navigation';
import { useNavigation } from '@/hooks/useNavigation';

/**
 * Navigation Test Component
 * Test component to verify navigation functionality
 */
export const NavigationTest: React.FC = () => {
  const { navigationState, navigateTo } = useNavigation();

  const testRoutes = [
    { path: '/', label: 'Home', page: 'main' },
    { path: '/chat', label: 'Chat', page: 'chat' },
    { path: '/notebooks', label: 'Notebooks', page: 'notebooks' },
    { path: '/files', label: 'Files', page: 'files' },
    { path: '/connections', label: 'Connections', page: 'connections' },
    { path: '/settings', label: 'Settings', page: 'settings' },
    { path: '/demo', label: 'Demo', page: 'demo' },
    { path: '/admin', label: 'Admin', page: 'admin' }
  ];

  const handleNavigateWithUtility = (path: string) => {
    navigateToPath(path);
  };

  const handleNavigateWithHook = (path: string) => {
    navigateTo(path);
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border">
      <h2 className="text-xl font-semibold mb-4">Navigation Test</h2>
      
      {/* Current State */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium mb-2">Current Navigation State:</h3>
        <div className="text-sm space-y-1">
          <p><strong>Current Page:</strong> {navigationState.currentPage}</p>
          <p><strong>Previous Page:</strong> {navigationState.previousPage || 'None'}</p>
          <p><strong>Current URL:</strong> {window.location.pathname}</p>
          <p><strong>Breadcrumbs:</strong> {navigationState.breadcrumbs.join(' > ')}</p>
        </div>
      </div>

      {/* Navigation with Utility */}
      <div className="mb-6">
        <h3 className="font-medium mb-3">Navigate with Utility Function:</h3>
        <div className="flex flex-wrap gap-2">
          {testRoutes.map((route) => (
            <Button
              key={route.path}
              size="sm"
              variant={navigationState.currentPage === route.page ? 'default' : 'outline'}
              onClick={() => handleNavigateWithUtility(route.path)}
            >
              {route.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Navigation with Hook */}
      <div className="mb-6">
        <h3 className="font-medium mb-3">Navigate with Hook:</h3>
        <div className="flex flex-wrap gap-2">
          {testRoutes.map((route) => (
            <Button
              key={`hook-${route.path}`}
              size="sm"
              variant={navigationState.currentPage === route.page ? 'default' : 'ghost'}
              onClick={() => handleNavigateWithHook(route.path)}
            >
              {route.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Browser Navigation */}
      <div>
        <h3 className="font-medium mb-3">Browser Navigation:</h3>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => window.history.back()}
          >
            ← Back
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => window.history.forward()}
          >
            Forward →
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => window.location.reload()}
          >
            Reload
          </Button>
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">Test Instructions:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Click buttons to test navigation</li>
          <li>• Check if URL changes correctly</li>
          <li>• Verify current page state updates</li>
          <li>• Test browser back/forward buttons</li>
          <li>• Check if page content reloads properly</li>
        </ul>
      </div>
    </div>
  );
};

export default NavigationTest;
