import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingSpinner } from '@/components/shared/ui';

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
  redirectTo?: string;
}

/**
 * ProtectedRoute component
 * Protects routes that require authentication
 * Optionally restricts access to admin users only
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  adminOnly = false,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Checking authentication..." />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location.pathname }} 
        replace 
      />
    );
  }

  // Check admin access if required
  if (adminOnly && user.role !== 'admin') {
    return (
      <Navigate 
        to="/" 
        state={{ error: 'Access denied. Admin privileges required.' }} 
        replace 
      />
    );
  }

  // Render protected content
  return <>{children}</>;
};

export default ProtectedRoute;
