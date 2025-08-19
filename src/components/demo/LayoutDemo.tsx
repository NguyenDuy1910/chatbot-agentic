import React from 'react';
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  Chip,
  Progress,
  Avatar,
  AvatarGroup,
  Divider,
  Badge,
  Spacer,
  Tabs,
  Tab,
} from '@heroui/react';
import {
  TrendingUp,
  Users,
  MessageSquare,
  Database,
  Activity,
  Calendar,
  FileText,
  BarChart3,
} from 'lucide-react';
import { ChatTrafficChart } from '@/components/charts/ChatTrafficChart';
import { UserActivityChart } from '@/components/charts/UserActivityChart';
import { APIUsageChart } from '@/components/charts/APIUsageChart';
import { RealTimeMetrics } from '@/components/charts/RealTimeMetrics';

export const LayoutDemo: React.FC = () => {
  const [selectedTab, setSelectedTab] = React.useState('overview');

  return (
    <div className="p-6 space-y-6">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to Vikki ChatBot</h1>
        <p className="text-lg opacity-90 mb-6">
          Your AI-powered data analysis platform with interactive analytics dashboard
        </p>
        <div className="flex gap-4">
          <Button color="secondary" variant="solid" size="lg">
            View Analytics
          </Button>
          <Button color="default" variant="bordered" size="lg">
            Learn More
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <Tabs
        selectedKey={selectedTab}
        onSelectionChange={(key) => setSelectedTab(key as string)}
        variant="underlined"
        color="primary"
        className="w-full"
      >
        <Tab key="overview" title="Overview" />
        <Tab key="analytics" title="Analytics" />
        <Tab key="realtime" title="Real-time" />
      </Tabs>

      {/* Content based on selected tab */}
      {selectedTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-none shadow-sm">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-default-500">Total Users</p>
                <p className="text-2xl font-bold">2,847</p>
                <div className="flex items-center gap-1 mt-1">
                  <TrendingUp className="h-4 w-4 text-success" />
                  <span className="text-sm text-success">+12%</span>
                </div>
              </div>
              <div className="p-3 bg-primary-100 rounded-lg">
                <Users className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardBody>
        </Card>

        <Card className="border-none shadow-sm">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-default-500">Chat Sessions</p>
                <p className="text-2xl font-bold">1,234</p>
                <div className="flex items-center gap-1 mt-1">
                  <TrendingUp className="h-4 w-4 text-success" />
                  <span className="text-sm text-success">+8%</span>
                </div>
              </div>
              <div className="p-3 bg-secondary-100 rounded-lg">
                <MessageSquare className="h-6 w-6 text-secondary" />
              </div>
            </div>
          </CardBody>
        </Card>

        <Card className="border-none shadow-sm">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-default-500">Data Sources</p>
                <p className="text-2xl font-bold">5</p>
                <div className="flex items-center gap-1 mt-1">
                  <Activity className="h-4 w-4 text-warning" />
                  <span className="text-sm text-warning">Active</span>
                </div>
              </div>
              <div className="p-3 bg-warning-100 rounded-lg">
                <Database className="h-6 w-6 text-warning" />
              </div>
            </div>
          </CardBody>
        </Card>

        <Card className="border-none shadow-sm">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-default-500">Notebooks</p>
                <p className="text-2xl font-bold">4</p>
                <div className="flex items-center gap-1 mt-1">
                  <FileText className="h-4 w-4 text-success" />
                  <span className="text-sm text-success">Ready</span>
                </div>
              </div>
              <div className="p-3 bg-success-100 rounded-lg">
                <BarChart3 className="h-6 w-6 text-success" />
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="lg:col-span-2 border-none shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Recent Activity</h3>
              <Button size="sm" variant="light" color="primary">
                View All
              </Button>
            </div>
          </CardHeader>
          <CardBody className="pt-0">
            <div className="space-y-4">
              {[
                { action: 'New chat session started', time: '2 minutes ago', user: 'John Doe' },
                { action: 'Notebook "Sales Analysis" updated', time: '15 minutes ago', user: 'Jane Smith' },
                { action: 'Data connector synchronized', time: '1 hour ago', user: 'System' },
                { action: 'New user registered', time: '2 hours ago', user: 'Mike Johnson' },
              ].map((activity, index) => (
                <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-default-50">
                  <Avatar name={activity.user} size="sm" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-default-500">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Team Members */}
        <Card className="border-none shadow-sm">
          <CardHeader className="pb-3">
            <h3 className="text-lg font-semibold">Team Members</h3>
          </CardHeader>
          <CardBody className="pt-0">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar name="Nguyễn Đình Quốc Duy" size="sm" />
                  <div>
                    <p className="text-sm font-medium">Nguyễn Đình Quốc Duy</p>
                    <p className="text-xs text-default-500">Admin</p>
                  </div>
                </div>
                <Chip size="sm" color="success" variant="flat">
                  Online
                </Chip>
              </div>
              
              <Divider />
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar name="John Doe" size="sm" />
                  <div>
                    <p className="text-sm font-medium">John Doe</p>
                    <p className="text-xs text-default-500">Analyst</p>
                  </div>
                </div>
                <Chip size="sm" color="warning" variant="flat">
                  Away
                </Chip>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar name="Jane Smith" size="sm" />
                  <div>
                    <p className="text-sm font-medium">Jane Smith</p>
                    <p className="text-xs text-default-500">Developer</p>
                  </div>
                </div>
                <Chip size="sm" color="default" variant="flat">
                  Offline
                </Chip>
              </div>
            </div>
            
            <Spacer y={4} />
            
            <Button color="primary" variant="flat" className="w-full">
              Invite Members
            </Button>
          </CardBody>
        </Card>
      </div>

      {/* Progress Section */}
      <Card className="border-none shadow-sm">
        <CardHeader>
          <h3 className="text-lg font-semibold">System Performance</h3>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">CPU Usage</span>
                <span className="text-sm text-default-500">45%</span>
              </div>
              <Progress value={45} color="primary" className="mb-1" />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Memory</span>
                <span className="text-sm text-default-500">67%</span>
              </div>
              <Progress value={67} color="warning" className="mb-1" />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Storage</span>
                <span className="text-sm text-default-500">23%</span>
              </div>
              <Progress value={23} color="success" className="mb-1" />
            </div>
          </div>
        </CardBody>
      </Card>
        </div>
      )}

      {/* Analytics Tab */}
      {selectedTab === 'analytics' && (
        <div className="space-y-8">
          {/* Chat Traffic Chart */}
          <ChatTrafficChart />

          {/* User Activity Chart */}
          <UserActivityChart />

          {/* API Usage Chart */}
          <APIUsageChart />
        </div>
      )}

      {/* Real-time Tab */}
      {selectedTab === 'realtime' && (
        <div className="space-y-6">
          <RealTimeMetrics />
        </div>
      )}
    </div>
  );
};
