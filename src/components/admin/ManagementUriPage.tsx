import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  ExternalLink, 
  Copy, 
  BarChart3, 
  Users, 
  MessageSquare, 
  Sparkles, 
  Settings,
  Home,
  Check
} from 'lucide-react';
import { AdminRouter, adminRoutes, useAdminRouter } from '@/lib/router';

const routeIcons: Record<string, React.ComponentType<any>> = {
  overview: Home,
  users: Users,
  chats: MessageSquare,
  prompts: Sparkles,
  settings: Settings
};

export const ManagementUriPage: React.FC = () => {
  const { currentRoute, navigateTo, buildUrl } = useAdminRouter();
  const [copiedUrl, setCopiedUrl] = React.useState<string | null>(null);

  const handleCopyUrl = async (route: string) => {
    const url = window.location.origin + buildUrl(route);
    try {
      await navigator.clipboard.writeText(url);
      setCopiedUrl(route);
      setTimeout(() => setCopiedUrl(null), 2000);
    } catch (error) {
      console.error('Failed to copy URL:', error);
    }
  };

  const handleNavigate = (route: string) => {
    navigateTo(route);
  };

  const routes = AdminRouter.getAllRoutes();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Management URI Directory</h1>
          <p className="text-muted-foreground">
            All available admin management pages and their URLs
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-sm">
            Current: {currentRoute}
          </Badge>
        </div>
      </div>

      {/* Current URL Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Current Page Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Current URL:</label>
              <div className="mt-1 p-3 bg-muted rounded-lg font-mono text-sm break-all">
                {window.location.href}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Active Route:</label>
              <div className="mt-1 flex items-center gap-2">
                <Badge className="text-sm">{currentRoute}</Badge>
                <span className="text-sm text-muted-foreground">
                  {adminRoutes[currentRoute]?.title}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Available Routes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {routes.map((route) => {
          const routeKey = Object.keys(adminRoutes).find(key => adminRoutes[key] === route);
          const IconComponent = routeKey ? routeIcons[routeKey] : Home;
          const isActive = currentRoute === routeKey;
          const fullUrl = window.location.origin + route.path;

          return (
            <Card key={route.path} className={`transition-all ${isActive ? 'ring-2 ring-primary' : ''}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <IconComponent className="h-5 w-5 text-primary" />
                  {route.title}
                  {isActive && (
                    <Badge className="ml-auto text-xs">Active</Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {route.description}
                </p>
                
                <div>
                  <label className="text-xs font-medium text-muted-foreground">URL:</label>
                  <div className="mt-1 p-2 bg-muted rounded text-xs font-mono break-all">
                    {fullUrl}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleNavigate(routeKey || 'overview')}
                    className="flex items-center gap-1"
                    disabled={isActive}
                  >
                    <ExternalLink className="h-3 w-3" />
                    {isActive ? 'Current Page' : 'Navigate'}
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopyUrl(routeKey || 'overview')}
                    className="flex items-center gap-1"
                  >
                    {copiedUrl === routeKey ? (
                      <>
                        <Check className="h-3 w-3 text-green-600" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        Copy URL
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* URL Patterns Info */}
      <Card>
        <CardHeader>
          <CardTitle>URL Pattern Guidelines</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-foreground mb-2">Base Routes:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li><code className="px-1 py-0.5 bg-muted rounded">/</code> - Main chatbot application</li>
                <li><code className="px-1 py-0.5 bg-muted rounded">/admin</code> - Admin dashboard overview</li>
                <li><code className="px-1 py-0.5 bg-muted rounded">/admin/*</code> - Admin management pages</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-foreground mb-2">Query Parameters:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li><code className="px-1 py-0.5 bg-muted rounded">?tab=users</code> - Direct tab navigation</li>
                <li><code className="px-1 py-0.5 bg-muted rounded">?filter=active</code> - Filter parameters</li>
                <li><code className="px-1 py-0.5 bg-muted rounded">?page=2</code> - Pagination parameters</li>
              </ul>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> This application uses client-side routing. URLs are managed 
                by the browser's History API for smooth navigation without page reloads.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ManagementUriPage;
