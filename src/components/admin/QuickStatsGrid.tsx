import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Users, MessageSquare, BarChart3, Calendar } from 'lucide-react';
import { AdminDashboardData } from '@/types/admin';

interface QuickStatsGridProps {
  statistics: AdminDashboardData['statistics'];
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  borderColor: string;
  iconColor: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, borderColor, iconColor }) => {
  return (
    <Card className={`${borderColor} border-l-4 hover:shadow-md transition-shadow duration-200`}>
      <CardContent className="p-4 sm:p-6">
        <div className="flex items-center justify-between">
          <div className="min-w-0 flex-1">
            <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">
              {value}
            </div>
            <div className="text-xs sm:text-sm text-muted-foreground mt-1 truncate">
              {title}
            </div>
          </div>
          <div className={`${iconColor} flex-shrink-0 ml-3`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const QuickStatsGrid: React.FC<QuickStatsGridProps> = ({ statistics }) => {
  const stats = [
    {
      title: 'Total Users',
      value: statistics.totalUsers,
      icon: <Users className="h-6 w-6 sm:h-8 sm:w-8" />,
      borderColor: 'border-l-blue-500',
      iconColor: 'text-blue-500'
    },
    {
      title: 'Active Now',
      value: statistics.activeUsers,
      icon: <MessageSquare className="h-6 w-6 sm:h-8 sm:w-8" />,
      borderColor: 'border-l-green-500',
      iconColor: 'text-green-500'
    },
    {
      title: 'Vikki Messages',
      value: statistics.totalMessages,
      icon: <BarChart3 className="h-6 w-6 sm:h-8 sm:w-8" />,
      borderColor: 'border-l-purple-500',
      iconColor: 'text-purple-500'
    },
    {
      title: 'Avg Session',
      value: `${statistics.averageSessionLength}m`,
      icon: <Calendar className="h-6 w-6 sm:h-8 sm:w-8" />,
      borderColor: 'border-l-orange-500',
      iconColor: 'text-orange-500'
    }
  ];

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mt-6">
        {stats.map((stat, index) => (
          <StatCard
            key={index}
            title={stat.title}
            value={stat.value}
            icon={stat.icon}
            borderColor={stat.borderColor}
            iconColor={stat.iconColor}
          />
        ))}
      </div>
    </div>
  );
};
