import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { StatisticsOverview } from '@/components/admin/StatisticsOverview';
import { ResponsiveLayout } from '@/components/admin/ResponsiveLayout';
import { Users, MessageSquare, Activity, Database, Cpu, HardDrive, Zap } from 'lucide-react';
import { AdminDashboardData } from '@/types/admin';

interface DashboardOverviewProps {
  statistics: AdminDashboardData['statistics'];
  users: AdminDashboardData['users'];
}

interface HealthMetricProps {
  label: string;
  value: string;
  status: 'healthy' | 'warning' | 'critical';
  icon?: React.ReactNode;
}

const HealthMetric: React.FC<HealthMetricProps> = ({ label, value, status, icon }) => {
  const statusColors = {
    healthy: 'text-green-600',
    warning: 'text-yellow-600',
    critical: 'text-red-600'
  };

  return (
    <div className="flex items-center justify-between py-2 px-1">
      <div className="flex items-center gap-2">
        {icon && <span className="text-muted-foreground">{icon}</span>}
        <span className="text-sm font-medium">{label}</span>
      </div>
      <span className={`text-sm font-semibold ${statusColors[status]}`}>
        {value}
      </span>
    </div>
  );
};

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({ 
  statistics, 
  users 
}) => {
  const recentUsers = users.slice(0, 5);
  
  const healthMetrics = [
    {
      label: 'Database',
      value: 'Healthy',
      status: 'healthy' as const,
      icon: <Database className="h-4 w-4" />
    },
    {
      label: 'API Response',
      value: '45ms avg',
      status: 'healthy' as const,
      icon: <Zap className="h-4 w-4" />
    },
    {
      label: 'Storage',
      value: '75% used',
      status: 'warning' as const,
      icon: <HardDrive className="h-4 w-4" />
    },
    {
      label: 'Memory',
      value: 'Normal',
      status: 'healthy' as const,
      icon: <Cpu className="h-4 w-4" />
    }
  ];

  return (
    <ResponsiveLayout>
      {/* Statistics Overview */}
      <StatisticsOverview statistics={statistics} />
      
      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Recent User Activity */}
        <Card className="lg:col-span-1 xl:col-span-2">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Users className="h-5 w-5 text-blue-500" />
              Recent User Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentUsers.length > 0 ? (
              recentUsers.map(user => (
                <div 
                  key={user.id} 
                  className="flex items-center justify-between p-3 border border-border/50 rounded-lg hover:bg-muted/30 transition-colors duration-200"
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium flex-shrink-0">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-foreground truncate">
                        {user.name}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {user.totalMessages} Vikki messages
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground flex-shrink-0 ml-2">
                    {new Date(user.lastActive).toLocaleDateString()}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No recent user activity</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Health */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Activity className="h-5 w-5 text-green-500" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {healthMetrics.map((metric, index) => (
                <HealthMetric
                  key={index}
                  label={metric.label}
                  value={metric.value}
                  status={metric.status}
                  icon={metric.icon}
                />
              ))}
            </div>
            
            {/* Overall Health Indicator */}
            <div className="mt-6 pt-4 border-t border-border/50">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Overall Status</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-semibold text-green-600">Operational</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-purple-500" />
            Quick Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border border-border/50 rounded-lg hover:bg-muted/20 transition-colors duration-200">
              <div className="text-2xl font-bold text-primary mb-1">
                {Math.round((statistics.activeUsers / statistics.totalUsers) * 100)}%
              </div>
              <div className="text-sm text-muted-foreground">User Engagement</div>
            </div>
            <div className="text-center p-4 border border-border/50 rounded-lg hover:bg-muted/20 transition-colors duration-200">
              <div className="text-2xl font-bold text-green-600 mb-1">
                {Math.round(statistics.totalMessages / statistics.totalUsers)}
              </div>
              <div className="text-sm text-muted-foreground">Avg Messages/User</div>
            </div>
            <div className="text-center p-4 border border-border/50 rounded-lg hover:bg-muted/20 transition-colors duration-200">
              <div className="text-2xl font-bold text-orange-600 mb-1">
                99.9%
              </div>
              <div className="text-sm text-muted-foreground">System Uptime</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </ResponsiveLayout>
  );
};
