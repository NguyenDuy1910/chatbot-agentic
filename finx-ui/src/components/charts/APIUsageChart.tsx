import React, { useState } from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  ButtonGroup,
  Chip,
  Tabs,
  Tab,
} from '@heroui/react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Zap, DollarSign, Clock, Activity } from 'lucide-react';
import { apiUsageData, getWeeklyData, getMonthlyData } from '@/data/mockChartData';

type ViewMode = 'daily' | 'weekly' | 'monthly';
type ChartType = 'calls' | 'tokens' | 'cost' | 'performance';

export const APIUsageChart: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('daily');
  const [chartType, setChartType] = useState<ChartType>('calls');

  const getData = () => {
    switch (viewMode) {
      case 'weekly':
        return getWeeklyData(apiUsageData, 'apiCalls');
      case 'monthly':
        return getMonthlyData(apiUsageData, 'apiCalls');
      default:
        return apiUsageData;
    }
  };

  const data = getData();
  const totalCalls = apiUsageData.reduce((sum, item) => sum + item.apiCalls, 0);
  const totalTokens = apiUsageData.reduce((sum, item) => sum + item.tokens, 0);
  const totalCost = apiUsageData.reduce((sum, item) => sum + item.cost, 0);
  const avgResponseTime = apiUsageData.reduce((sum, item) => sum + item.avgResponseTime, 0) / apiUsageData.length;

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
                  {entry.name.includes('Cost') 
                    ? `$${entry.value.toFixed(2)}`
                    : entry.name.includes('Time')
                    ? `${entry.value.toFixed(0)}ms`
                    : entry.value.toLocaleString()
                  }
                </span>
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  const getChartData = () => {
    switch (chartType) {
      case 'tokens':
        return { dataKey: 'tokens', name: 'Tokens Used', color: 'hsl(var(--heroui-secondary))' };
      case 'cost':
        return { dataKey: 'cost', name: 'Cost ($)', color: 'hsl(var(--heroui-warning))' };
      case 'performance':
        return { dataKey: 'avgResponseTime', name: 'Response Time (ms)', color: 'hsl(var(--heroui-danger))' };
      default:
        return { dataKey: 'apiCalls', name: 'API Calls', color: 'hsl(var(--heroui-primary))' };
    }
  };

  const chartConfig = getChartData();

  return (
    <Card className="border-none shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-warning-100 rounded-lg">
              <Zap className="h-5 w-5 text-warning" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">API & Token Usage</h3>
              <p className="text-sm text-default-500">LLM API consumption and performance metrics</p>
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
            <div className="p-2 bg-primary-100 rounded-lg">
              <Zap className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-sm text-default-500">Total API Calls</p>
              <p className="text-lg font-semibold text-foreground">{totalCalls.toLocaleString()}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-secondary-100 rounded-lg">
              <Activity className="h-4 w-4 text-secondary" />
            </div>
            <div>
              <p className="text-sm text-default-500">Total Tokens</p>
              <p className="text-lg font-semibold text-foreground">{(totalTokens / 1000000).toFixed(1)}M</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-warning-100 rounded-lg">
              <DollarSign className="h-4 w-4 text-warning" />
            </div>
            <div>
              <p className="text-sm text-default-500">Total Cost</p>
              <p className="text-lg font-semibold text-foreground">${totalCost.toFixed(2)}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-3 bg-default-50 rounded-lg">
            <div className="p-2 bg-danger-100 rounded-lg">
              <Clock className="h-4 w-4 text-danger" />
            </div>
            <div>
              <p className="text-sm text-default-500">Avg Response</p>
              <p className="text-lg font-semibold text-foreground">{avgResponseTime.toFixed(0)}ms</p>
            </div>
          </div>
        </div>

        {/* Chart Type Tabs */}
        <Tabs 
          selectedKey={chartType} 
          onSelectionChange={(key) => setChartType(key as ChartType)}
          className="mb-4"
          variant="underlined"
          color="primary"
        >
          <Tab key="calls" title="API Calls" />
          <Tab key="tokens" title="Token Usage" />
          <Tab key="cost" title="Cost Analysis" />
          <Tab key="performance" title="Performance" />
        </Tabs>

        {/* Chart */}
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            {chartType === 'performance' ? (
              <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
                <Line
                  type="monotone"
                  dataKey={chartConfig.dataKey}
                  stroke={chartConfig.color}
                  strokeWidth={3}
                  dot={{ fill: chartConfig.color, strokeWidth: 2, r: 4 }}
                  name={chartConfig.name}
                />
              </LineChart>
            ) : (
              <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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
                <Bar
                  dataKey={chartConfig.dataKey}
                  fill={chartConfig.color}
                  name={chartConfig.name}
                  radius={[2, 2, 0, 0]}
                  opacity={0.8}
                />
              </BarChart>
            )}
          </ResponsiveContainer>
        </div>

        {/* Cost Breakdown & Insights */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-divider">
          <div className="flex items-center gap-4">
            <Chip size="sm" color="success" variant="flat">
              Efficiency: +15%
            </Chip>
            <Chip size="sm" color="warning" variant="flat">
              Cost per token: $0.00002
            </Chip>
            <Chip size="sm" color="primary" variant="flat">
              Peak usage: 2-4 PM
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
