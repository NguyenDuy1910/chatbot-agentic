import React, { useState, useEffect } from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Chip,
  Progress,
  Avatar,
  AvatarGroup,
} from '@heroui/react';
import {
  Activity,
  Users,
  MessageSquare,
  Zap,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';
import { generateRealTimeData } from '@/data/mockChartData';

interface MetricCardProps {
  title: string;
  value: string | number;
  change: number;
  icon: React.ReactNode;
  color: 'primary' | 'success' | 'warning' | 'danger';
  suffix?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  change, 
  icon, 
  color,
  suffix = ''
}) => {
  const getTrendIcon = () => {
    if (change > 0) return <TrendingUp className="h-3 w-3" />;
    if (change < 0) return <TrendingDown className="h-3 w-3" />;
    return <Minus className="h-3 w-3" />;
  };

  const getTrendColor = () => {
    if (change > 0) return 'success';
    if (change < 0) return 'danger';
    return 'default';
  };

  return (
    <Card className="border-none shadow-sm">
      <CardBody className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className={`p-2 bg-${color}-100 rounded-lg`}>
            {icon}
          </div>
          <Chip
            size="sm"
            variant="flat"
            color={getTrendColor()}
            startContent={getTrendIcon()}
          >
            {change > 0 ? '+' : ''}{change.toFixed(1)}%
          </Chip>
        </div>
        <div>
          <p className="text-2xl font-bold text-foreground">
            {typeof value === 'number' ? value.toLocaleString() : value}{suffix}
          </p>
          <p className="text-sm text-default-500">{title}</p>
        </div>
      </CardBody>
    </Card>
  );
};

export const RealTimeMetrics: React.FC = () => {
  const [metrics, setMetrics] = useState(generateRealTimeData());
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(generateRealTimeData());
      setLastUpdate(new Date());
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const systemHealth = 95; // Mock system health percentage
  const activeConnections = 5;
  const queuedTasks = 12;

  return (
    <div className="space-y-6">
      {/* Real-time Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Sessions"
          value={metrics.currentSessions}
          change={8.5}
          icon={<MessageSquare className="h-5 w-5 text-primary" />}
          color="primary"
        />
        
        <MetricCard
          title="Online Users"
          value={metrics.activeUsers}
          change={12.3}
          icon={<Users className="h-5 w-5 text-success" />}
          color="success"
        />
        
        <MetricCard
          title="API Calls/min"
          value={metrics.apiCallsPerMinute}
          change={-2.1}
          icon={<Zap className="h-5 w-5 text-warning" />}
          color="warning"
        />
        
        <MetricCard
          title="Response Time"
          value={metrics.avgResponseTime}
          change={-5.7}
          icon={<Activity className="h-5 w-5 text-danger" />}
          color="danger"
          suffix="ms"
        />
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Health */}
        <Card className="border-none shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-success-100 rounded-lg">
                <Activity className="h-5 w-5 text-success" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">System Health</h3>
                <p className="text-sm text-default-500">Overall system performance</p>
              </div>
            </div>
          </CardHeader>
          <CardBody className="pt-0">
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Overall Health</span>
                  <span className="text-sm text-success font-semibold">{systemHealth}%</span>
                </div>
                <Progress 
                  value={systemHealth} 
                  color="success" 
                  className="mb-1"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-default-500">CPU Usage</p>
                  <p className="font-semibold">45%</p>
                </div>
                <div>
                  <p className="text-default-500">Memory</p>
                  <p className="font-semibold">67%</p>
                </div>
                <div>
                  <p className="text-default-500">Storage</p>
                  <p className="font-semibold">23%</p>
                </div>
                <div>
                  <p className="text-default-500">Network</p>
                  <p className="font-semibold text-success">Optimal</p>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Active Connections */}
        <Card className="border-none shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Zap className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Data Sources</h3>
                <p className="text-sm text-default-500">Connected databases</p>
              </div>
            </div>
          </CardHeader>
          <CardBody className="pt-0">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-foreground">{activeConnections}</span>
                <Chip size="sm" color="success" variant="flat">
                  All Online
                </Chip>
              </div>
              
              <div className="space-y-3">
                {[
                  { name: 'PostgreSQL', status: 'connected', latency: '12ms' },
                  { name: 'MongoDB', status: 'connected', latency: '8ms' },
                  { name: 'Redis Cache', status: 'connected', latency: '3ms' },
                  { name: 'Elasticsearch', status: 'connected', latency: '15ms' },
                  { name: 'S3 Storage', status: 'connected', latency: '45ms' },
                ].map((connection, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-default-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-success rounded-full" />
                      <span className="text-sm font-medium">{connection.name}</span>
                    </div>
                    <span className="text-xs text-default-500">{connection.latency}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Recent Activity */}
        <Card className="border-none shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-warning-100 rounded-lg">
                <Users className="h-5 w-5 text-warning" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Live Activity</h3>
                <p className="text-sm text-default-500">Current user sessions</p>
              </div>
            </div>
          </CardHeader>
          <CardBody className="pt-0">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Active Users</span>
                <AvatarGroup isBordered max={3} size="sm">
                  <Avatar name="John Doe" />
                  <Avatar name="Jane Smith" />
                  <Avatar name="Mike Johnson" />
                  <Avatar name="Sarah Wilson" />
                  <Avatar name="Tom Brown" />
                </AvatarGroup>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-default-500">Queued Tasks</span>
                  <Chip size="sm" variant="flat" color="warning">
                    {queuedTasks}
                  </Chip>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-default-500">Processing</span>
                  <Chip size="sm" variant="flat" color="primary">
                    3
                  </Chip>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-default-500">Completed Today</span>
                  <Chip size="sm" variant="flat" color="success">
                    247
                  </Chip>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Last Update Info */}
      <div className="flex items-center justify-between text-xs text-default-500">
        <span>Real-time data updates every 5 seconds</span>
        <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
      </div>
    </div>
  );
};
