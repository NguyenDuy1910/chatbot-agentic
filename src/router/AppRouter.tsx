import React, { Suspense } from 'react';
import { AppShell } from '@/components/shared/layout/AppShell';
import { LoadingSpinner } from '@/components/shared/ui';
// import { LoginPage } from '@/pages'; // Temporarily disabled
// import { useAuth } from '@/contexts/AuthContext'; // Temporarily disabled

/**
 * Enhanced router with AppShell layout
 * Uses AppShell for static layout with dynamic main content
 */
export const AppRouter: React.FC = () => {
  // const { user, isAuthenticated } = useAuth?.() || { user: null, isAuthenticated: false }; // Temporarily disabled

  // Mock user data - replace with actual user context
  const user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    role: 'admin'
  };

  // Loading component for suspense
  const SuspenseLoader = () => (
    <div className="min-h-screen flex items-center justify-center">
      <LoadingSpinner size="lg" text="Loading application..." />
    </div>
  );

  return (
    <Suspense fallback={<SuspenseLoader />}>
      <AppShell
        user={user}
        showFooter={true}
        showExtendedFooter={false}
        onUserMenuClick={() => console.log('User menu clicked')}
      />
    </Suspense>
  );
};

export default AppRouter;
