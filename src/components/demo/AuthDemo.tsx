import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/shared/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/shared/ui/Card';
import { Input } from '@/components/shared/ui/Input';
import { Badge } from '@/components/shared/ui/Badge';

/**
 * AuthDemo component for testing authentication functionality
 */
export const AuthDemo: React.FC = () => {
  const { user, isAuthenticated, loading, error, login, register, logout } = useAuth();
  const [loginForm, setLoginForm] = useState({
    email: 'demo@vikki.com',
    password: 'demo123'
  });
  const [registerForm, setRegisterForm] = useState({
    name: 'New User',
    email: 'newuser@example.com',
    password: 'password123',
    confirmPassword: 'password123'
  });

  const handleLogin = async () => {
    try {
      await login({
        email: loginForm.email,
        password: loginForm.password,
        rememberMe: false
      });
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleRegister = async () => {
    try {
      await register({
        name: registerForm.name,
        email: registerForm.email,
        password: registerForm.password,
        confirmPassword: registerForm.confirmPassword
      });
    } catch (err) {
      console.error('Register failed:', err);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold text-center">Authentication Demo</h1>
      
      {/* Current Status */}
      <Card>
        <CardHeader>
          <CardTitle>Current Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <span>Authentication Status:</span>
            <Badge variant={isAuthenticated ? "default" : "secondary"}>
              {isAuthenticated ? "Authenticated" : "Not Authenticated"}
            </Badge>
          </div>
          
          {loading && (
            <div className="text-blue-600">Loading...</div>
          )}
          
          {error && (
            <div className="text-red-600 p-3 bg-red-50 rounded-lg">
              Error: {error}
            </div>
          )}
          
          {user && (
            <div className="space-y-2">
              <h3 className="font-semibold">User Information:</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><strong>ID:</strong> {user.id}</div>
                <div><strong>Name:</strong> {user.name}</div>
                <div><strong>Email:</strong> {user.email}</div>
                <div><strong>Role:</strong> {user.role}</div>
                <div><strong>Status:</strong> {user.status}</div>
                <div><strong>Avatar:</strong> {user.avatar || 'None'}</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Login Form */}
      {!isAuthenticated && (
        <Card>
          <CardHeader>
            <CardTitle>Login Test</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <Input
                  type="email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="Enter email"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Password</label>
                <Input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
                  placeholder="Enter password"
                />
              </div>
            </div>
            <Button onClick={handleLogin} disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Register Form */}
      {!isAuthenticated && (
        <Card>
          <CardHeader>
            <CardTitle>Register Test</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <Input
                  type="text"
                  value={registerForm.name}
                  onChange={(e) => setRegisterForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <Input
                  type="email"
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm(prev => ({ ...prev, email: e.target.value }))}
                  placeholder="Enter email"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Password</label>
                <Input
                  type="password"
                  value={registerForm.password}
                  onChange={(e) => setRegisterForm(prev => ({ ...prev, password: e.target.value }))}
                  placeholder="Enter password"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Confirm Password</label>
                <Input
                  type="password"
                  value={registerForm.confirmPassword}
                  onChange={(e) => setRegisterForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  placeholder="Confirm password"
                />
              </div>
            </div>
            <Button onClick={handleRegister} disabled={loading}>
              {loading ? 'Registering...' : 'Register'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Logout */}
      {isAuthenticated && (
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={handleLogout} variant="destructive" disabled={loading}>
              {loading ? 'Logging out...' : 'Logout'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AuthDemo;
