import React, { Suspense } from 'react';
import { ChatPage, AdminPage, ConnectionsPage } from '@/pages';
// import { LoginPage } from '@/pages'; // Temporarily disabled
// import { useAuth } from '@/contexts/AuthContext'; // Temporarily disabled

/**
 * Enhanced router with authentication and lazy loading support
 */
export const AppRouter: React.FC = () => {
  const path = window.location.pathname;
  // const { user, isAuthenticated } = useAuth?.() || { user: null, isAuthenticated: false }; // Temporarily disabled

  // Loading component for suspense
  const LoadingSpinner = () => (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>
  );

  // Protected route wrapper - TEMPORARILY DISABLED FOR DEVELOPMENT
  const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({
    children,
    adminOnly = false
  }) => {
    // TODO: Re-enable authentication when needed
    // if (!isAuthenticated) {
    //   return <LoginPage />;
    // }

    // if (adminOnly && user?.role !== 'admin') {
    //   return (
    //     <div className="min-h-screen flex items-center justify-center">
    //       <div className="text-center">
    //         <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
    //         <p className="text-gray-600">You don't have permission to access this page.</p>
    //       </div>
    //     </div>
    //   );
    // }

    return <>{children}</>;
  };

  // Route matching logic - AUTHENTICATION TEMPORARILY DISABLED
  const renderRoute = () => {
    switch (true) {
      // case path === '/login':
      //   return <LoginPage />; // Temporarily disabled

      case path.startsWith('/admin'):
        return (
          <ProtectedRoute adminOnly>
            <AdminPage />
          </ProtectedRoute>
        );

      case path.startsWith('/connections'):
        return (
          <ProtectedRoute>
            <ConnectionsPage />
          </ProtectedRoute>
        );

      case path === '/' || path.startsWith('/chat'):
        return (
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        );

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
    <Suspense fallback={<LoadingSpinner />}>
      {renderRoute()}
    </Suspense>
  );
};

export default AppRouter;
