import React, { useState } from 'react';
import { ChatStatistics } from '@/types/features/admin';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/shared/ui/Card';
import { Badge } from '@/components/shared/ui/Badge';
import { 
  BarChart3, 
  TrendingUp, 
  MessageSquare, 
  Users,
  Calendar,
  Activity
} from 'lucide-react';

interface ChatVisualizationProps {
  statistics: ChatStatistics;
}

export const ChatVisualization: React.FC<ChatVisualizationProps> = ({ statistics }) => {
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d'>('7d');

  const maxMessages = Math.max(...statistics.messagesByDay.map(d => d.count));
  const maxUsers = Math.max(...statistics.userGrowth.map(d => d.count));

  return (
    <div className="space-y-6">
      {/* Chart Period Selector */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Chat Analytics
        </h3>
        <div className="flex items-center gap-2">
          {(['7d', '30d', '90d'] as const).map(period => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                selectedPeriod === period
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {period === '7d' ? 'Last 7 days' : period === '30d' ? 'Last 30 days' : 'Last 90 days'}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Messages Per Day Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-blue-500" />
              Messages Per Day
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="h-48 flex items-end justify-between gap-2">
                {statistics.messagesByDay.map((day, index) => {
                  const height = (day.count / maxMessages) * 100;
                  return (
                    <div key={index} className="flex-1 flex flex-col items-center group">
                      <div 
                        className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-sm transition-all duration-300 hover:from-blue-600 hover:to-blue-500 cursor-pointer"
                        style={{ height: `${height}%`, minHeight: '4px' }}
                        title={`${new Date(day.date).toLocaleDateString()}: ${day.count} messages`}
                      />
                      <div className="text-xs text-muted-foreground mt-2 transform rotate-45 origin-center">
                        {new Date(day.date).toLocaleDateString('en', { weekday: 'short' })}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>0</span>
                <span>{maxMessages}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* User Growth Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              User Growth
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="h-48 flex items-end justify-between gap-2">
                {statistics.userGrowth.map((month, index) => {
                  const height = (month.count / maxUsers) * 100;
                  return (
                    <div key={index} className="flex-1 flex flex-col items-center group">
                      <div 
                        className="w-full bg-gradient-to-t from-green-500 to-green-400 rounded-t-sm transition-all duration-300 hover:from-green-600 hover:to-green-500 cursor-pointer"
                        style={{ height: `${height}%`, minHeight: '4px' }}
                        title={`${month.date}: ${month.count} users`}
                      />
                      <div className="text-xs text-muted-foreground mt-2 transform rotate-45 origin-center">
                        {month.date.split('-')[1]}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>0</span>
                <span>{maxUsers}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Popular Prompts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-purple-500" />
            Popular Prompts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {statistics.popularPrompts.map((prompt, index) => {
              const popularity = ((statistics.popularPrompts.length - index) / statistics.popularPrompts.length) * 100;
              return (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">
                      {prompt}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      #{index + 1}
                    </Badge>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-purple-500 to-purple-400 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${popularity}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="text-center">
          <CardContent className="pt-6">
            <Users className="h-8 w-8 mx-auto mb-2 text-blue-500" />
            <div className="text-2xl font-bold text-foreground">{statistics.activeUsers}</div>
            <div className="text-sm text-muted-foreground">Active Users</div>
          </CardContent>
        </Card>
        
        <Card className="text-center">
          <CardContent className="pt-6">
            <MessageSquare className="h-8 w-8 mx-auto mb-2 text-green-500" />
            <div className="text-2xl font-bold text-foreground">{statistics.totalChats}</div>
            <div className="text-sm text-muted-foreground">Total Chats</div>
          </CardContent>
        </Card>
        
        <Card className="text-center">
          <CardContent className="pt-6">
            <Calendar className="h-8 w-8 mx-auto mb-2 text-purple-500" />
            <div className="text-2xl font-bold text-foreground">{statistics.averageSessionLength}m</div>
            <div className="text-sm text-muted-foreground">Avg Session</div>
          </CardContent>
        </Card>
        
        <Card className="text-center">
          <CardContent className="pt-6">
            <TrendingUp className="h-8 w-8 mx-auto mb-2 text-orange-500" />
            <div className="text-2xl font-bold text-foreground">+24.5%</div>
            <div className="text-sm text-muted-foreground">Growth Rate</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
