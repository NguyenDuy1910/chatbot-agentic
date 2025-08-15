import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { useAdminRouter } from '@/lib/router';

interface BreadcrumbProps {
  className?: string;
}

export const AdminBreadcrumb: React.FC<BreadcrumbProps> = ({ className = '' }) => {
  const { getBreadcrumbs, navigateTo } = useAdminRouter();
  const breadcrumbs = getBreadcrumbs();

  return (
    <nav className={`flex items-center space-x-1 text-sm text-muted-foreground ${className}`}>
      <button
        onClick={() => navigateTo('overview')}
        className="flex items-center gap-1 hover:text-foreground transition-colors"
      >
        <Home className="h-4 w-4" />
        <span>Admin</span>
      </button>
      
      {breadcrumbs.length > 1 && (
        <>
          {breadcrumbs.slice(1).map((crumb) => (
            <React.Fragment key={crumb.path}>
              <ChevronRight className="h-4 w-4" />
              <button
                onClick={() => {
                  // Extract route name from path
                  const routeName = crumb.path.split('/').pop() || 'overview';
                  navigateTo(routeName);
                }}
                className="hover:text-foreground transition-colors"
              >
                {crumb.title}
              </button>
            </React.Fragment>
          ))}
        </>
      )}
    </nav>
  );
};

export default AdminBreadcrumb;
