import React, { useState } from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  ButtonGroup,
  Chip,
  Progress,
} from '@heroui/react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Users, UserPlus, TrendingUp, Target } from 'lucide-react';
import { userActivityData, getWeeklyData, getMonthlyData } from '@/data/mockChartData';

type ViewMode = 'daily' | 'weekly' | 'monthly';

export const UserActivityChart: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('daily');

  const getData = () => {
    switch (viewMode) {
      case 'weekly':
        return getWeeklyData(userActivityData, 'activeUsers');
      case 'monthly':
        return getMonthlyData(userActivityData, 'activeUsers');
      default:
        return userActivityData;
    }
  };

  const data = getData();
  const totalActiveUsers = userActivityData.reduce((sum, item) => sum + item.activeUsers, 0);
  const avgActiveUsers = Math.floor(totalActiveUsers / userActivityData.length);
  const totalNewUsers = userActivityData.reduce((sum, item) => sum + item.newRegistrations, 0);
  const avgRetention = userActivityData.reduce((sum, item) => sum + item.retention, 0) / userActivityData.length;

  const formatXAxisLabel = (tickItem: string) => {
    if (viewMode === 'monthly') {
      return new Date(tickItem + '-01').toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
    }
    if (viewMode === 'weekly') {
      return tickItem.split(' - ')[0].substring(5); // MM-DD
    }
    return new Date(tickItem).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-divider rounded-lg p-3 shadow-lg">
          <p className="text-sm font-medium text-foreground mb-2">
            {viewMode === 'monthly' 
              ? new Date(label + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
              : viewMode === 'weekly'
              ? `Week: ${label}`
              : new Date(label).toLocaleDateString('en-US', { 
                  weekday: 'short', 
                  month: 'short', 
                  day: 'numeric' 
                })
            }
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm text-default-600">
                {entry.name}: <span className="font-medium text-foreground">
                  {entry.name === 'Retention Rate' ? `${entry.value.toFixed(1)}%` : entry.value.toLocaleString()}
                </span>
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="border-none shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-success-100 rounded-lg">
              <Users className="h-5 w-5 text-success" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">User Activity</h3>
              <p className="text-sm text-default-500">Engagement metrics and user growth</p>
            </div>
          </div>
          <ButtonGroup size="sm" variant="flat">
            <Button
              color={viewMode === 'daily' ? 'primary' : 'default'}
              onPress={() => setViewMode('daily')}
            >
              Daily
            </Button>
            <Button
              color={viewMode === 'weekly' ? 'primary' : 'default'}
              onPress={() => setViewMode('weekly')}
            >
              Weekly
            </Button>
            <Button
              color={viewMode === 'monthly' ? 'primary' : 'default'}
              onPress={() => setViewMode('monthly')}
            >
              Monthly
            </Button>
          </ButtonGroup>
        </div>
      </CardHeader>
      <CardBody className="pt-0">
        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-success-100 rounded-lg">
              <Users className="h-4 w-4 text-success" />
            </div>
            <div>
              <p className="text-sm text-default-500">Avg Active Users</p>
              <p className="text-lg font-semibold text-foreground">{avgActiveUsers}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-primary-100 rounded-lg">
              <UserPlus className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-sm text-default-500">New Users</p>
              <p className="text-lg font-semibold text-foreground">{totalNewUsers}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-warning-100 rounded-lg">
              <Target className="h-4 w-4 text-warning" />
            </div>
            <div>
              <p className="text-sm text-default-500">Avg Retention</p>
              <p className="text-lg font-semibold text-foreground">{avgRetention.toFixed(1)}%</p>
            </div>
          </div>

          <div className="p-3 bg-default-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-default-500">Growth Rate</p>
              <TrendingUp className="h-4 w-4 text-success" />
            </div>
            <Progress 
              value={78} 
              color="success" 
              className="mb-1"
              size="sm"
            />
            <p className="text-xs text-success">+8.5% this month</p>
          </div>
        </div>

        {/* Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--heroui-divider))" />
              <XAxis 
                dataKey="date" 
                tickFormatter={formatXAxisLabel}
                stroke="hsl(var(--heroui-default-500))"
                fontSize={12}
              />
              <YAxis 
                yAxisId="left"
                stroke="hsl(var(--heroui-default-500))" 
                fontSize={12} 
              />
              <YAxis 
                yAxisId="right" 
                orientation="right"
                stroke="hsl(var(--heroui-default-500))" 
                fontSize={12}
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar
                yAxisId="left"
                dataKey="activeUsers"
                fill="hsl(var(--heroui-success))"
                name="Active Users"
                radius={[2, 2, 0, 0]}
                opacity={0.8}
              />
              <Bar
                yAxisId="left"
                dataKey="newRegistrations"
                fill="hsl(var(--heroui-primary))"
                name="New Registrations"
                radius={[2, 2, 0, 0]}
                opacity={0.8}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="retention"
                stroke="hsl(var(--heroui-warning))"
                strokeWidth={3}
                dot={{ fill: 'hsl(var(--heroui-warning))', strokeWidth: 2, r: 4 }}
                name="Retention Rate (%)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Insights */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-divider">
          <div className="flex items-center gap-4">
            <Chip size="sm" color="success" variant="flat">
              <TrendingUp className="h-3 w-3 mr-1" />
              User growth +8.5%
            </Chip>
            <Chip size="sm" color="warning" variant="flat">
              Retention: {avgRetention.toFixed(1)}%
            </Chip>
            <Chip size="sm" color="primary" variant="flat">
              Peak activity: Weekdays
            </Chip>
          </div>
          <p className="text-xs text-default-500">
            Last updated: {new Date().toLocaleTimeString()}
          </p>
        </div>
      </CardBody>
    </Card>
  );
};
