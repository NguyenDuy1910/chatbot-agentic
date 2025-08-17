import React, { useState } from 'react';
import { authAPI } from '@/lib/authAPI';
import { connectionAPI } from '@/lib/connectionAPI';
import { promptAPI } from '@/lib/promptAPI';
import { chatAPI } from '@/lib/chatAPI';
import { api } from '@/lib/api';

interface TestResult {
  name: string;
  status: 'idle' | 'loading' | 'success' | 'error';
  result?: any;
  error?: string;
  duration?: number;
}

export const APIIntegrationDemo: React.FC = () => {
  const [tests, setTests] = useState<TestResult[]>([
    { name: 'Health Check', status: 'idle' },
    { name: 'Auth - Login', status: 'idle' },
    { name: 'Auth - Get User', status: 'idle' },
    { name: 'Connections - List', status: 'idle' },
    { name: 'Prompts - List', status: 'idle' },
    { name: 'Chats - List', status: 'idle' },
    { name: 'Messages - List', status: 'idle' },
  ]);

  const updateTest = (name: string, updates: Partial<TestResult>) => {
    setTests(prev => prev.map(test => 
      test.name === name ? { ...test, ...updates } : test
    ));
  };

  const runTest = async (name: string, testFn: () => Promise<any>) => {
    updateTest(name, { status: 'loading' });
    const startTime = Date.now();
    
    try {
      const result = await testFn();
      const duration = Date.now() - startTime;
      updateTest(name, { 
        status: 'success', 
        result, 
        duration 
      });
    } catch (error) {
      const duration = Date.now() - startTime;
      updateTest(name, { 
        status: 'error', 
        error: error instanceof Error ? error.message : String(error),
        duration 
      });
    }
  };

  const testHealthCheck = () => runTest('Health Check', async () => {
    return await api.get('/health');
  });

  const testAuthLogin = () => runTest('Auth - Login', async () => {
    return await authAPI.login({
      email: 'demo@vikki.com',
      password: 'demo123'
    });
  });

  const testAuthGetUser = () => runTest('Auth - Get User', async () => {
    return await authAPI.getCurrentUser();
  });

  const testConnectionsList = () => runTest('Connections - List', async () => {
    return await connectionAPI.getConnections();
  });

  const testPromptsList = () => runTest('Prompts - List', async () => {
    return await promptAPI.getPrompts();
  });

  const testChatsList = () => runTest('Chats - List', async () => {
    return await chatAPI.getChats();
  });

  const testMessagesList = () => runTest('Messages - List', async () => {
    return await chatAPI.getMessages();
  });

  const runAllTests = async () => {
    await testHealthCheck();
    await testAuthLogin();
    await testAuthGetUser();
    await testConnectionsList();
    await testPromptsList();
    await testChatsList();
    await testMessagesList();
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'idle': return '⚪';
      case 'loading': return '🔄';
      case 'success': return '✅';
      case 'error': return '❌';
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'idle': return 'text-gray-500';
      case 'loading': return 'text-blue-500';
      case 'success': return 'text-green-500';
      case 'error': return 'text-red-500';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          🧪 API Integration Demo
        </h1>
        <p className="text-gray-600 mb-6">
          Test các API endpoints đã được tích hợp với backend
        </p>

        <div className="flex gap-4 mb-6">
          <button
            onClick={runAllTests}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium"
          >
            🚀 Run All Tests
          </button>
          <button
            onClick={() => setTests(prev => prev.map(test => ({ ...test, status: 'idle', result: undefined, error: undefined })))}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium"
          >
            🔄 Reset
          </button>
        </div>

        <div className="space-y-4">
          {tests.map((test) => (
            <div key={test.name} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{getStatusIcon(test.status)}</span>
                  <span className={`font-medium ${getStatusColor(test.status)}`}>
                    {test.name}
                  </span>
                  {test.duration && (
                    <span className="text-sm text-gray-500">
                      ({test.duration}ms)
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  {test.name === 'Health Check' && (
                    <button
                      onClick={testHealthCheck}
                      className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
                    >
                      Test
                    </button>
                  )}
                  {test.name === 'Auth - Login' && (
                    <button
                      onClick={testAuthLogin}
                      className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
                    >
                      Test
                    </button>
                  )}
                  {test.name === 'Auth - Get User' && (
                    <button
                      onClick={testAuthGetUser}
                      className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
                    >
                      Test
                    </button>
                  )}
                  {test.name === 'Connections - List' && (
                    <button
                      onClick={testConnectionsList}
                      className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
                    >
                      Test
                    </button>
                  )}
                  {test.name === 'Prompts - List' && (
                    <button
                      onClick={testPromptsList}
                      className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
                    >
                      Test
                    </button>
                  )}
                  {test.name === 'Chats - List' && (
                    <button
                      onClick={testChatsList}
                      className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
                    >
                      Test
                    </button>
                  )}
                  {test.name === 'Messages - List' && (
                    <button
                      onClick={testMessagesList}
                      className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded"
                    >
                      Test
                    </button>
                  )}
                </div>
              </div>

              {test.error && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  <strong>Error:</strong> {test.error}
                </div>
              )}

              {test.result && (
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded">
                  <details>
                    <summary className="text-sm font-medium text-green-700 cursor-pointer">
                      View Result
                    </summary>
                    <pre className="mt-2 text-xs text-green-600 overflow-auto">
                      {JSON.stringify(test.result, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">📝 Notes:</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Backend server phải đang chạy trên http://localhost:8000</li>
            <li>• Database connection phải được setup đúng</li>
            <li>• Demo credentials: demo@vikki.com / demo123</li>
            <li>• Một số endpoints có thể cần authentication trước</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
