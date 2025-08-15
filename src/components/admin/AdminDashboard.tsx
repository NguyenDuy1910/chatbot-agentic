import React, { useState, useEffect } from 'react';
import { AdminDashboardData, User, SystemSettings } from '@/types/admin';
import { TabsContent } from '@/components/ui/Tabs';
import { UserManagement } from '@/components/admin/UserManagement';
import { ChatVisualization } from '@/components/admin/ChatVisualization';
import { SystemSettingsPanel } from '@/components/admin/SystemSettings';
import { AdminPromptManagement } from '@/components/admin/AdminPromptManagement';
import { ManagementUriPage } from '@/components/admin/ManagementUriPage';
import { DashboardHeader } from '@/components/admin/DashboardHeader';
import { QuickStatsGrid } from '@/components/admin/QuickStatsGrid';
import { LoadingState, ErrorState } from '@/components/admin/DashboardStates';
import { DashboardOverview } from '@/components/admin/DashboardOverview';
import { DashboardTabs } from '@/components/admin/DashboardTabs';
import { ResponsiveLayout } from '@/components/admin/ResponsiveLayout';
import { adminAPI } from '@/lib/adminAPI';
import { useAdminRouter } from '@/lib/router';

export const AdminDashboard: React.FC = () => {
  const { currentRoute, navigateTo } = useAdminRouter();
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const data = await adminAPI.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDashboardData();
    setIsRefreshing(false);
  };

  const handleUpdateUserStatus = async (userId: string, status: User['status']) => {
    if (!dashboardData) return;
    
    try {
      await adminAPI.updateUserStatus(userId, status);
      setDashboardData(prev => {
        if (!prev) return null;
        return {
          ...prev,
          users: prev.users.map(user => 
            user.id === userId ? { ...user, status } : user
          )
        };
      });
    } catch (error) {
      console.error('Failed to update user status:', error);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!dashboardData) return;

    try {
      await adminAPI.deleteUser(userId);
      setDashboardData(prev => {
        if (!prev) return null;
        return {
          ...prev,
          users: prev.users.filter(user => user.id !== userId)
        };
      });
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  const handleUpdateSettings = async (settings: Partial<SystemSettings>) => {
    if (!dashboardData) return;

    try {
      const updatedSettings = await adminAPI.updateSettings(settings);
      setDashboardData(prev => {
        if (!prev) return null;
        return {
          ...prev,
          settings: updatedSettings
        };
      });
    } catch (error) {
      console.error('Failed to update settings:', error);
      throw error;
    }
  };

  const handleViewUserChats = (userId: string) => {
    // Navigate to Vikki chatbot conversation view or open modal
    console.log('View Vikki chatbot conversations for user:', userId);
    // This could open a modal or navigate to a detailed view
  };

  const exportReport = () => {
    if (!dashboardData) return;

    const report = {
      generatedAt: new Date().toISOString(),
      statistics: dashboardData.statistics,
      userCount: dashboardData.users.length,
      activeUsers: dashboardData.users.filter(u => u.status === 'active').length,
      settings: dashboardData.settings
    };

    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `admin-report-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Loading State
  if (isLoading) {
    return <LoadingState />;
  }

  // Error State
  if (!dashboardData) {
    return <ErrorState onRetry={loadDashboardData} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/10">
      {/* Header */}
      <DashboardHeader
        onExportReport={exportReport}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
      />

      {/* Quick Stats */}
      <QuickStatsGrid statistics={dashboardData.statistics} />

      {/* Main Content with Tabs */}
      <div className="py-6">
        <DashboardTabs activeTab={currentRoute} onTabChange={navigateTo}>
          <TabsContent value="overview">
            <DashboardOverview
              statistics={dashboardData.statistics}
              users={dashboardData.users}
            />
          </TabsContent>

          <TabsContent value="users">
            <ResponsiveLayout>
              <UserManagement
                users={dashboardData.users}
                onUpdateUserStatus={handleUpdateUserStatus}
                onDeleteUser={handleDeleteUser}
                onViewUserChats={handleViewUserChats}
              />
            </ResponsiveLayout>
          </TabsContent>

          <TabsContent value="chats">
            <ResponsiveLayout>
              <ChatVisualization statistics={dashboardData.statistics} />
            </ResponsiveLayout>
          </TabsContent>

          <TabsContent value="prompts">
            <ResponsiveLayout>
              <AdminPromptManagement />
            </ResponsiveLayout>
          </TabsContent>

          <TabsContent value="settings">
            <ResponsiveLayout>
              <SystemSettingsPanel
                settings={dashboardData.settings}
                onUpdateSettings={handleUpdateSettings}
              />
            </ResponsiveLayout>
          </TabsContent>

          <TabsContent value="uris">
            <ResponsiveLayout>
              <ManagementUriPage />
            </ResponsiveLayout>
          </TabsContent>
        </DashboardTabs>
      </div>
    </div>
  );
};
