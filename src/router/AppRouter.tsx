import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from '@/components/shared/layout/AppShell';
import { LoadingSpinner } from '@/components/shared/ui';
import { ProtectedRoute } from '@/components/shared/auth';
import { useAuth } from '@/contexts/AuthContext';
import { ROUTES } from './constants';
import { LoginPage } from '@/pages';

/**
 * Enhanced router with authentication and protected routes
 * Uses AppShell for authenticated users, direct routing for login
 */
export const AppRouter: React.FC = () => {
  const { user, isAuthenticated, loading, logout } = useAuth();

  // Loading component for suspense
  const SuspenseLoader = () => (
    <div className="min-h-screen flex items-center justify-center">
      <LoadingSpinner size="lg" text="Loading application..." />
    </div>
  );

  // Show loading while checking authentication
  if (loading) {
    return <SuspenseLoader />;
  }

  return (
    <BrowserRouter>
      <Suspense fallback={<SuspenseLoader />}>
        <Routes>
          {/* Login route - accessible to all */}
          <Route
            path={ROUTES.LOGIN}
            element={
              isAuthenticated ? (
                <Navigate to={ROUTES.HOME} replace />
              ) : (
                <LoginPage />
              )
            }
          />

          {/* All other routes wrapped in AppShell for authenticated users */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppShell
                  user={user ? {
                    name: user.name,
                    email: user.email,
                    avatar: user.avatar,
                    role: user.role
                  } : undefined}
                  showFooter={true}
                  showExtendedFooter={false}
                  onUserMenuClick={() => logout()}
                />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};

export default AppRouter;
