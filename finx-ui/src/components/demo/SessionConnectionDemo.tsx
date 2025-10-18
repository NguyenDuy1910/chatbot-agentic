import React, { useState } from 'react';
import { Card, CardBody, CardHeader, Button, Divider, Chip, Badge } from '@heroui/react';
import { useAuth } from '@/contexts/AuthContext';
import { useConnection } from '@/contexts/ConnectionContext';
import { LoginCredentials } from '@/types/features/auth';
import { Lock, Unlock, Database, CheckCircle, XCircle, User, LogOut } from 'lucide-react';

/**
 * Demo component to test login and connection session management
 */
export const SessionConnectionDemo: React.FC = () => {
  const { user, isAuthenticated, login, logout, loading: authLoading } = useAuth();
  const { connections, currentConnection, addConnection, clearConnections } = useConnection();
  
  const [loginForm, setLoginForm] = useState<LoginCredentials>({
    email: 'demo@vikki.com',
    password: 'demo123',
    rememberMe: false
  });

  const handleLogin = async () => {
    try {
      await login(loginForm);
      console.log('✅ Login successful');
    } catch (error) {
      console.error('❌ Login failed:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      console.log('✅ Logout successful');
    } catch (error) {
      console.error('❌ Logout failed:', error);
    }
  };

  const handleTestConnection = () => {
    // Simulate a test connection
    addConnection({
      name: `Demo Connection ${connections.length + 1}`,
      type: 'athena',
      config: {
        region: 'us-east-1',
        accessKeyId: 'DEMO_KEY',
        secretAccessKey: 'DEMO_SECRET',
        outputLocation: 's3://demo-bucket/output/'
      },
      isDefault: connections.length === 0,
      metadata: {
        catalog: 'AwsDataCatalog',
        region: 'us-east-1'
      }
    });
    console.log('✅ Connection added to session');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card className="shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <div className="flex items-center gap-3">
            <Database className="h-6 w-6" />
            <div>
              <h2 className="text-xl font-bold">Session Connection Management Demo</h2>
              <p className="text-sm opacity-90">Test login and connection caching</p>
            </div>
          </div>
        </CardHeader>

        <CardBody className="space-y-6">
          {/* Authentication Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                {isAuthenticated ? (
                  <>
                    <Unlock className="h-5 w-5 text-green-500" />
                    Authentication Status
                  </>
                ) : (
                  <>
                    <Lock className="h-5 w-5 text-gray-400" />
                    Authentication Status
                  </>
                )}
              </h3>
              <Chip 
                color={isAuthenticated ? "success" : "default"} 
                variant="flat"
                startContent={isAuthenticated ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
              >
                {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
              </Chip>
            </div>

            {!isAuthenticated ? (
              <Card className="bg-gray-50">
                <CardBody className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Email</label>
                    <input
                      type="email"
                      value={loginForm.email}
                      onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="demo@vikki.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Password</label>
                    <input
                      type="password"
                      value={loginForm.password}
                      onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                      placeholder="demo123"
                    />
                  </div>
                  <Button
                    color="primary"
                    size="lg"
                    onClick={handleLogin}
                    isLoading={authLoading}
                    className="w-full"
                  >
                    Login
                  </Button>
                </CardBody>
              </Card>
            ) : (
              <Card className="bg-green-50 border border-green-200">
                <CardBody className="space-y-4">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center text-white">
                      <User className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-lg">{user?.name}</p>
                      <p className="text-sm text-gray-600">{user?.email}</p>
                      <Badge color="primary" variant="flat" className="mt-2">
                        {user?.role}
                      </Badge>
                    </div>
                  </div>
                  <Button
                    color="danger"
                    variant="flat"
                    size="lg"
                    onClick={handleLogout}
                    startContent={<LogOut className="h-4 w-4" />}
                    className="w-full"
                  >
                    Logout
                  </Button>
                </CardBody>
              </Card>
            )}
          </div>

          <Divider />

          {/* Session Connections Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Database className="h-5 w-5 text-blue-500" />
                Session Connections
              </h3>
              <Chip color="primary" variant="flat">
                {connections.length} saved
              </Chip>
            </div>

            {isAuthenticated ? (
              <>
                <div className="space-y-3 mb-4">
                  {connections.length === 0 ? (
                    <Card className="bg-gray-50">
                      <CardBody className="text-center py-8">
                        <Database className="h-12 w-12 mx-auto text-gray-400 mb-3" />
                        <p className="text-gray-600">No connections in session</p>
                        <p className="text-sm text-gray-500 mt-1">
                          Test a connection to save it to this session
                        </p>
                      </CardBody>
                    </Card>
                  ) : (
                    connections.map((conn) => (
                      <Card 
                        key={conn.id} 
                        className={`${currentConnection?.id === conn.id ? 'border-2 border-blue-500' : ''}`}
                      >
                        <CardBody className="flex flex-row items-center justify-between">
                          <div>
                            <p className="font-semibold flex items-center gap-2">
                              {conn.name}
                              {conn.isDefault && (
                                <Chip size="sm" color="primary" variant="flat">Default</Chip>
                              )}
                              {currentConnection?.id === conn.id && (
                                <Chip size="sm" color="success" variant="flat">Active</Chip>
                              )}
                            </p>
                            <p className="text-sm text-gray-600">
                              {conn.type.toUpperCase()} • {conn.metadata?.region || 'N/A'} • 
                              {conn.metadata?.catalog || 'N/A'}
                            </p>
                          </div>
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        </CardBody>
                      </Card>
                    ))
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    color="primary"
                    onClick={handleTestConnection}
                    className="flex-1"
                  >
                    Add Demo Connection
                  </Button>
                  {connections.length > 0 && (
                    <Button
                      color="danger"
                      variant="flat"
                      onClick={clearConnections}
                    >
                      Clear All
                    </Button>
                  )}
                </div>
              </>
            ) : (
              <Card className="bg-yellow-50 border border-yellow-200">
                <CardBody className="text-center py-6">
                  <Lock className="h-8 w-8 mx-auto text-yellow-600 mb-2" />
                  <p className="text-yellow-800 font-medium">Please login first</p>
                  <p className="text-sm text-yellow-700 mt-1">
                    Connections are only available after authentication
                  </p>
                </CardBody>
              </Card>
            )}
          </div>

          <Divider />

          {/* Info Section */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">How It Works</h3>
            <div className="text-sm space-y-2 text-gray-600">
              <div className="flex gap-2">
                <span className="font-semibold min-w-[30px]">1.</span>
                <span>Login với credentials (mock auth đã tắt)</span>
              </div>
              <div className="flex gap-2">
                <span className="font-semibold min-w-[30px]">2.</span>
                <span>Test connections → auto-save vào sessionStorage</span>
              </div>
              <div className="flex gap-2">
                <span className="font-semibold min-w-[30px]">3.</span>
                <span>Connections persist trong cùng session (tab)</span>
              </div>
              <div className="flex gap-2">
                <span className="font-semibold min-w-[30px]">4.</span>
                <span>Logout → tất cả connections bị xóa</span>
              </div>
            </div>
          </div>

          {/* SessionStorage Info */}
          <Card className="bg-blue-50 border border-blue-200">
            <CardBody>
              <p className="text-sm font-semibold text-blue-900 mb-2">💡 SessionStorage Info</p>
              <div className="text-sm text-blue-800 space-y-1">
                <p>✅ Data persists khi refresh page</p>
                <p>✅ Automatically cleared khi đóng tab</p>
                <p>✅ Separate cho mỗi browser tab</p>
                <p>✅ Secure - không share giữa các tabs</p>
              </div>
            </CardBody>
          </Card>
        </CardBody>
      </Card>
    </div>
  );
};

export default SessionConnectionDemo;
