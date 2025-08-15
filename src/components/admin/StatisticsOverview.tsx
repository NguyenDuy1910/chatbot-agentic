import React from 'react';
import { ChatStatistics } from '@/types/admin';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Clock,
  Activity,
  BarChart3
} from 'lucide-react';

interface StatisticsOverviewProps {
  statistics: ChatStatistics;
}

export const StatisticsOverview: React.FC<StatisticsOverviewProps> = ({ statistics }) => {
  const stats = [
    {
      title: 'Total Users',
      value: statistics.totalUsers.toLocaleString(),
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      change: '+12.5%',
      changeType: 'positive' as const
    },
    {
      title: 'Total Chats',
      value: statistics.totalChats.toLocaleString(),
      icon: MessageSquare,
      color: 'from-green-500 to-green-600',
      change: '+8.2%',
      changeType: 'positive' as const
    },
    {
      title: 'Total Messages',
      value: statistics.totalMessages.toLocaleString(),
      icon: BarChart3,
      color: 'from-purple-500 to-purple-600',
      change: '+15.3%',
      changeType: 'positive' as const
    },
    {
      title: 'Active Users',
      value: statistics.activeUsers.toLocaleString(),
      icon: Activity,
      color: 'from-orange-500 to-orange-600',
      change: '+5.7%',
      changeType: 'positive' as const
    },
    {
      title: 'Avg Session Length',
      value: `${statistics.averageSessionLength}m`,
      icon: Clock,
      color: 'from-red-500 to-red-600',
      change: '-2.1%',
      changeType: 'negative' as const
    },
    {
      title: 'Growth Rate',
      value: '24.5%',
      icon: TrendingUp,
      color: 'from-indigo-500 to-indigo-600',
      change: '+3.4%',
      changeType: 'positive' as const
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <Card key={index} className="relative overflow-hidden hover:shadow-lg transition-shadow duration-300">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-lg bg-gradient-to-r ${stat.color} shadow-lg`}>
                  <Icon className="h-4 w-4 text-white" />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-foreground">
                  {stat.value}
                </div>
                <div className="flex items-center space-x-2 text-xs">
                  <span 
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      stat.changeType === 'positive' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {stat.change}
                  </span>
                  <span className="text-muted-foreground">from last month</span>
                </div>
              </div>
            </CardContent>
            
            {/* Decorative gradient overlay */}
            <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${stat.color} opacity-60`} />
          </Card>
        );
      })}
    </div>
  );
};
