import React, { useState } from 'react';
import { authAPI } from '@/lib/authAPI';
import { UserProfile } from '@/types/features/auth';

export const LoginDemo: React.FC = () => {
  const [email, setEmail] = useState('demo@vikki.com');
  const [password, setPassword] = useState('demo123');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await authAPI.login({ email, password });
      setUser(response.user);
      setSuccess('Login successful!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await authAPI.logout();
      setUser(null);
      setSuccess('Logged out successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGetCurrentUser = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
      setSuccess('User data retrieved!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        🔐 Authentication Demo
      </h2>

      {!user ? (
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white py-2 px-4 rounded-md font-medium"
          >
            {loading ? '🔄 Logging in...' : '🚀 Login'}
          </button>
        </form>
      ) : (
        <div className="space-y-4">
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-medium text-green-900 mb-2">✅ Logged in as:</h3>
            <div className="text-sm text-green-700">
              <p><strong>Name:</strong> {user.name}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Role:</strong> {user.role}</p>
              <p><strong>ID:</strong> {user.id}</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleGetCurrentUser}
              disabled={loading}
              className="flex-1 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-300 text-white py-2 px-4 rounded-md font-medium text-sm"
            >
              {loading ? '🔄' : '👤'} Refresh User
            </button>
            <button
              onClick={handleLogout}
              disabled={loading}
              className="flex-1 bg-red-500 hover:bg-red-600 disabled:bg-red-300 text-white py-2 px-4 rounded-md font-medium text-sm"
            >
              {loading ? '🔄' : '🚪'} Logout
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">
            <strong>❌ Error:</strong> {error}
          </p>
        </div>
      )}

      {success && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-700 text-sm">
            <strong>✅ Success:</strong> {success}
          </p>
        </div>
      )}

      <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-medium text-blue-900 text-sm mb-1">💡 Demo Credentials:</h4>
        <p className="text-blue-700 text-xs">
          Email: demo@vikki.com<br />
          Password: demo123
        </p>
      </div>
    </div>
  );
};
