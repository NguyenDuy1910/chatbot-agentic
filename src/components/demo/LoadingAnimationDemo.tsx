import React, { useState } from 'react';
import { Button } from '@/components/shared/ui';
import { 
  LoadingSpinner, 
  PageTransition, 
  SkeletonLoader, 
  SkeletonCard, 
  SkeletonTable, 
  SkeletonGrid 
} from '@/components/shared/ui';
import { navigateToPath } from '@/lib/navigation';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Loader2,
  Sparkles,
  Zap
} from 'lucide-react';

/**
 * Loading Animation Demo Component
 * Demonstrates all loading animations and transitions
 */
export const LoadingAnimationDemo: React.FC = () => {
  const [isPageLoading, setIsPageLoading] = useState(false);
  const [isSpinnerVisible, setIsSpinnerVisible] = useState(false);
  const [isSkeletonVisible, setIsSkeletonVisible] = useState(false);

  const handlePageTransitionDemo = () => {
    setIsPageLoading(true);
    setTimeout(() => setIsPageLoading(false), 2000);
  };

  const handleSpinnerDemo = () => {
    setIsSpinnerVisible(true);
    setTimeout(() => setIsSpinnerVisible(false), 3000);
  };

  const handleSkeletonDemo = () => {
    setIsSkeletonVisible(true);
    setTimeout(() => setIsSkeletonVisible(false), 4000);
  };

  const handleNavigationDemo = (path: string, loadingText: string) => {
    navigateToPath(path, {
      showLoading: true,
      loadingText,
      loadingDuration: 1500
    });
  };

  const testRoutes = [
    { path: '/chat', label: 'Chat', loadingText: 'Loading Chat Interface...' },
    { path: '/notebooks', label: 'Notebooks', loadingText: 'Loading Notebooks...' },
    { path: '/files', label: 'Files', loadingText: 'Loading File Manager...' },
    { path: '/connections', label: 'Connections', loadingText: 'Loading Data Connections...' },
    { path: '/settings', label: 'Settings', loadingText: 'Loading Settings...' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-xl font-semibold mb-2">Loading Animation Demo</h2>
        <p className="text-gray-600">
          Comprehensive demonstration of loading animations, transitions, and skeleton loaders
        </p>
      </div>

      {/* Loading Spinners */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Loading Spinners</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="text-center">
            <h4 className="font-medium mb-3">Small</h4>
            <LoadingSpinner size="sm" />
          </div>
          <div className="text-center">
            <h4 className="font-medium mb-3">Medium</h4>
            <LoadingSpinner size="md" />
          </div>
          <div className="text-center">
            <h4 className="font-medium mb-3">Large</h4>
            <LoadingSpinner size="lg" />
          </div>
          <div className="text-center">
            <h4 className="font-medium mb-3">Extra Large</h4>
            <LoadingSpinner size="xl" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="text-center">
            <h4 className="font-medium mb-3">With Text</h4>
            <LoadingSpinner size="md" text="Loading data..." />
          </div>
          <div className="text-center">
            <h4 className="font-medium mb-3">Interactive Demo</h4>
            <Button onClick={handleSpinnerDemo} className="mb-3">
              <Play className="h-4 w-4 mr-2" />
              Show Spinner (3s)
            </Button>
            {isSpinnerVisible && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <LoadingSpinner size="lg" text="Demo loading..." />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Page Transitions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Page Transitions</h3>
        
        <div className="mb-6">
          <Button onClick={handlePageTransitionDemo} className="mb-4">
            <Sparkles className="h-4 w-4 mr-2" />
            Demo Page Transition (2s)
          </Button>
          
          <PageTransition isLoading={isPageLoading} loadingText="Loading page content...">
            <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Page Content</h4>
              <p className="text-gray-600">
                This content appears with a smooth transition animation after loading completes.
                The transition includes fade-in and slide-up effects for a polished user experience.
              </p>
              <div className="flex items-center space-x-2 mt-4">
                <Zap className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-blue-600 font-medium">Smooth & Fast</span>
              </div>
            </div>
          </PageTransition>
        </div>
      </div>

      {/* Skeleton Loaders */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Skeleton Loaders</h3>
        
        <div className="mb-6">
          <Button onClick={handleSkeletonDemo} className="mb-4">
            <Loader2 className="h-4 w-4 mr-2" />
            Demo Skeleton Loading (4s)
          </Button>
        </div>

        {isSkeletonVisible ? (
          <div className="space-y-6">
            <div>
              <h4 className="font-medium mb-3">Card Skeleton</h4>
              <SkeletonCard />
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Table Skeleton</h4>
              <SkeletonTable rows={3} columns={4} />
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Grid Skeleton</h4>
              <SkeletonGrid items={3} />
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <h4 className="font-medium mb-3">Basic Skeletons</h4>
              <div className="space-y-3">
                <SkeletonLoader variant="text" />
                <SkeletonLoader variant="text" lines={3} />
                <div className="flex items-center space-x-3">
                  <SkeletonLoader variant="circular" width={40} height={40} />
                  <div className="flex-1">
                    <SkeletonLoader variant="text" width="60%" />
                    <SkeletonLoader variant="text" width="40%" />
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Card Example</h4>
              <div className="max-w-md">
                <SkeletonCard />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Loading Demo */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Navigation Loading</h3>
        <p className="text-gray-600 mb-6">
          Test navigation with loading animations. Click any button to see the loading animation in action.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {testRoutes.map((route) => (
            <Button
              key={route.path}
              variant="outline"
              onClick={() => handleNavigationDemo(route.path, route.loadingText)}
              className="justify-start"
            >
              <Play className="h-4 w-4 mr-2" />
              {route.label}
            </Button>
          ))}
        </div>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">How it works:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Click any navigation button to trigger loading animation</li>
            <li>• Loading spinner appears with custom text</li>
            <li>• Page transitions smoothly after loading</li>
            <li>• URL updates and content loads with animation</li>
          </ul>
        </div>
      </div>

      {/* Animation Controls */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Animation Controls</h3>
        
        <div className="flex flex-wrap gap-3">
          <Button onClick={handlePageTransitionDemo}>
            <Play className="h-4 w-4 mr-2" />
            Page Transition
          </Button>
          <Button onClick={handleSpinnerDemo} variant="outline">
            <RotateCcw className="h-4 w-4 mr-2" />
            Spinner Demo
          </Button>
          <Button onClick={handleSkeletonDemo} variant="outline">
            <Loader2 className="h-4 w-4 mr-2" />
            Skeleton Demo
          </Button>
          <Button 
            onClick={() => window.location.reload()} 
            variant="ghost"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset All
          </Button>
        </div>
      </div>
    </div>
  );
};

export default LoadingAnimationDemo;
