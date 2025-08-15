import React, { useState, useEffect } from 'react';
import { AdminDashboardData, User, SystemSettings } from '@/types/admin';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { StatisticsOverview } from '@/components/admin/StatisticsOverview';
import { UserManagement } from '@/components/admin/UserManagement';
import { ChatVisualization } from '@/components/admin/ChatVisualization';
import { SystemSettingsPanel } from '@/components/admin/SystemSettings';
import { AdminPromptManagement } from '@/components/admin/AdminPromptManagement';
import { adminAPI } from '@/lib/adminAPI';
import { 
  BarChart3, 
  Users, 
  Settings, 
  Sparkles, 
  MessageSquare,
  Shield,
  RefreshCw,
  Download,
  Calendar,
  Crown
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
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
    // Navigate to user chat view or open modal
    console.log('View chats for user:', userId);
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <div className="text-lg font-medium">Loading Admin Dashboard...</div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Shield className="h-8 w-8 mx-auto mb-4 text-red-500" />
          <div className="text-lg font-medium">Failed to load dashboard data</div>
          <Button onClick={loadDashboardData} className="mt-4">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/10">
      {/* Header */}
      <div className="border-b border-border/50 bg-gradient-to-r from-background/80 to-muted/20 backdrop-blur-sm">
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent flex items-center gap-3">
                <Crown className="h-8 w-8 text-primary" />
                Admin Dashboard
              </h1>
              <p className="text-muted-foreground mt-2">
                Manage users, monitor chats, and configure system settings
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button 
                variant="outline" 
                onClick={exportReport}
                className="flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Export Report
              </Button>
              <Button 
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="flex items-center gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <Card className="border-l-4 border-l-blue-500">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-foreground">
                      {dashboardData.statistics.totalUsers}
                    </div>
                    <div className="text-sm text-muted-foreground">Total Users</div>
                  </div>
                  <Users className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-green-500">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-foreground">
                      {dashboardData.statistics.activeUsers}
                    </div>
                    <div className="text-sm text-muted-foreground">Active Now</div>
                  </div>
                  <MessageSquare className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-purple-500">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-foreground">
                      {dashboardData.statistics.totalMessages}
                    </div>
                    <div className="text-sm text-muted-foreground">Messages</div>
                  </div>
                  <BarChart3 className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-orange-500">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-foreground">
                      {dashboardData.statistics.averageSessionLength}m
                    </div>
                    <div className="text-sm text-muted-foreground">Avg Session</div>
                  </div>
                  <Calendar className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5 lg:w-auto lg:inline-flex mb-6">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Users
            </TabsTrigger>
            <TabsTrigger value="chats" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="prompts" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Prompts
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="space-y-6">
              <StatisticsOverview statistics={dashboardData.statistics} />
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5 text-blue-500" />
                      Recent User Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {dashboardData.users.slice(0, 5).map(user => (
                        <div key={user.id} className="flex items-center justify-between p-2 border rounded">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium">
                              {user.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <div className="font-medium">{user.name}</div>
                              <div className="text-sm text-muted-foreground">{user.totalMessages} messages</div>
                            </div>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(user.lastActive).toLocaleDateString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="h-5 w-5 text-green-500" />
                      System Health
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Database</span>
                        <span className="text-sm font-medium text-green-600">Healthy</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">API Response</span>
                        <span className="text-sm font-medium text-green-600">45ms avg</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Storage</span>
                        <span className="text-sm font-medium text-yellow-600">75% used</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Memory</span>
                        <span className="text-sm font-medium text-green-600">Normal</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="users">
            <UserManagement
              users={dashboardData.users}
              onUpdateUserStatus={handleUpdateUserStatus}
              onDeleteUser={handleDeleteUser}
              onViewUserChats={handleViewUserChats}
            />
          </TabsContent>

          <TabsContent value="chats">
            <ChatVisualization statistics={dashboardData.statistics} />
          </TabsContent>

          <TabsContent value="prompts">
            <AdminPromptManagement />
          </TabsContent>

          <TabsContent value="settings">
            <SystemSettingsPanel
              settings={dashboardData.settings}
              onUpdateSettings={handleUpdateSettings}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
