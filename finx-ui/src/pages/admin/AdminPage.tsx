import React from 'react';
import { AdminDashboard } from '@/components/features/admin';

/**
 * Admin page component - content only
 * Handles admin dashboard and management features
 */
export const AdminPage: React.FC = () => {
  return (
    <div className="p-6">
      <AdminDashboard />
    </div>
  );
};

export default AdminPage;
