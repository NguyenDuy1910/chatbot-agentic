import React, { useState } from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  ButtonGroup,
  Chip,
} from '@heroui/react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { MessageSquare, TrendingUp, Clock } from 'lucide-react';
import { chatTrafficData, getWeeklyData, getMonthlyData } from '@/data/mockChartData';

type ViewMode = 'daily' | 'weekly' | 'monthly';

export const ChatTrafficChart: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('daily');

  const getData = () => {
    switch (viewMode) {
      case 'weekly':
        return getWeeklyData(chatTrafficData, 'sessions');
      case 'monthly':
        return getMonthlyData(chatTrafficData, 'sessions');
      default:
        return chatTrafficData;
    }
  };

  const data = getData();
  const totalSessions = chatTrafficData.reduce((sum, item) => sum + item.sessions, 0);
  const avgSessions = Math.floor(totalSessions / chatTrafficData.length);
  const totalMessages = chatTrafficData.reduce((sum, item) => sum + item.messages, 0);

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
                {entry.name}: <span className="font-medium text-foreground">{entry.value.toLocaleString()}</span>
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
            <div className="p-2 bg-primary-100 rounded-lg">
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">Chat Traffic</h3>
              <p className="text-sm text-default-500">Session volume and message activity</p>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-primary-100 rounded-lg">
              <MessageSquare className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-sm text-default-500">Total Sessions</p>
              <p className="text-lg font-semibold text-foreground">{totalSessions.toLocaleString()}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-success-100 rounded-lg">
              <TrendingUp className="h-4 w-4 text-success" />
            </div>
            <div>
              <p className="text-sm text-default-500">Avg Daily Sessions</p>
              <p className="text-lg font-semibold text-foreground">{avgSessions}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-warning-100 rounded-lg">
              <Clock className="h-4 w-4 text-warning" />
            </div>
            <div>
              <p className="text-sm text-default-500">Total Messages</p>
              <p className="text-lg font-semibold text-foreground">{Math.floor(totalMessages).toLocaleString()}</p>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="sessionsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--heroui-primary))" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="hsl(var(--heroui-primary))" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="messagesGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--heroui-secondary))" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="hsl(var(--heroui-secondary))" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--heroui-divider))" />
              <XAxis 
                dataKey="date" 
                tickFormatter={formatXAxisLabel}
                stroke="hsl(var(--heroui-default-500))"
                fontSize={12}
              />
              <YAxis stroke="hsl(var(--heroui-default-500))" fontSize={12} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="sessions"
                stroke="hsl(var(--heroui-primary))"
                fillOpacity={1}
                fill="url(#sessionsGradient)"
                strokeWidth={2}
                name="Chat Sessions"
              />
              <Area
                type="monotone"
                dataKey="messages"
                stroke="hsl(var(--heroui-secondary))"
                fillOpacity={1}
                fill="url(#messagesGradient)"
                strokeWidth={2}
                name="Messages"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Trend Indicators */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-divider">
          <div className="flex items-center gap-4">
            <Chip size="sm" color="success" variant="flat">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12% vs last period
            </Chip>
            <Chip size="sm" color="primary" variant="flat">
              Peak: 2-4 PM
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
