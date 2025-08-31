import React, { useState } from 'react';
import { AppLayout } from './AppLayout';

/**
 * Demo component để test unified layout system
 * Hiển thị tất cả các tính năng của layout template
 */
export const LayoutDemo: React.FC = () => {
  const [currentPage, setCurrentPage] = useState('main');
  const [showExtendedFooter, setShowExtendedFooter] = useState(false);

  // Mock user data
  const user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    avatar: '',
    role: 'admin'
  };

  const handleNavigate = (path: string) => {
    // Extract page from path
    const page = path === '/' ? 'main' : path.substring(1);
    setCurrentPage(page);
  };

  const renderPageContent = () => {
    switch (currentPage) {
      case 'main':
        return (
          <div className="p-6">
            <div className="max-w-4xl mx-auto">
              <h1 className="text-3xl font-bold text-gray-900 mb-6">
                Welcome to Vikki ChatBot
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-semibold mb-3">🤖 AI Chat</h3>
                  <p className="text-gray-600 mb-4">
                    Interact with our intelligent chatbot for instant assistance.
                  </p>
                  <button 
                    onClick={() => handleNavigate('/chat')}
                    className="julius-btn julius-btn-primary"
                  >
                    Start Chat
                  </button>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-semibold mb-3">🔗 Connections</h3>
                  <p className="text-gray-600 mb-4">
                    Manage your data sources and integrations.
                  </p>
                  <button 
                    onClick={() => handleNavigate('/connections')}
                    className="julius-btn julius-btn-secondary"
                  >
                    View Connections
                  </button>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-semibold mb-3">⚙️ Admin</h3>
                  <p className="text-gray-600 mb-4">
                    Access admin dashboard and system settings.
                  </p>
                  <button 
                    onClick={() => handleNavigate('/admin')}
                    className="julius-btn julius-btn-secondary"
                  >
                    Admin Panel
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      case 'chat':
        return (
          <div className="p-6">
            <div className="max-w-4xl mx-auto">
              <h1 className="text-2xl font-bold text-gray-900 mb-6">Chat Interface</h1>
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="space-y-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-blue-800">
                      <strong>You:</strong> Hello, how can you help me today?
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-800">
                      <strong>Vikki:</strong> Hi! I'm here to help you with any questions or tasks you have. 
                      What would you like to know?
                    </p>
                  </div>
                </div>
                <div className="mt-6 flex space-x-2">
                  <input
                    type="text"
                    placeholder="Type your message..."
                    className="flex-1 julius-search-input"
                  />
                  <button className="julius-btn julius-btn-primary">Send</button>
                </div>
              </div>
            </div>
          </div>
        );

      case 'connections':
        return (
          <div className="p-6">
            <div className="max-w-6xl mx-auto">
              <h1 className="text-2xl font-bold text-gray-900 mb-6">Data Connections</h1>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'API Gateway'].map((conn) => (
                  <div key={conn} className="bg-white p-4 rounded-lg shadow-sm border">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium">{conn}</h3>
                      <span className="julius-badge julius-badge-green">Connected</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      Active connection to {conn} database
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'admin':
        return (
          <div className="p-6">
            <div className="max-w-6xl mx-auto">
              <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Dashboard</h1>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-semibold text-gray-900">Users</h3>
                  <p className="text-3xl font-bold text-blue-600 mt-2">1,234</p>
                  <p className="text-sm text-gray-600">Total registered users</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-semibold text-gray-900">Messages</h3>
                  <p className="text-3xl font-bold text-green-600 mt-2">45,678</p>
                  <p className="text-sm text-gray-600">Messages processed</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-semibold text-gray-900">Connections</h3>
                  <p className="text-3xl font-bold text-purple-600 mt-2">23</p>
                  <p className="text-sm text-gray-600">Active connections</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h3 className="text-lg font-semibold text-gray-900">Uptime</h3>
                  <p className="text-3xl font-bold text-orange-600 mt-2">99.9%</p>
                  <p className="text-sm text-gray-600">System availability</p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="p-6">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">Page: {currentPage}</h1>
              <p className="text-gray-600">This is a demo page for the unified layout system.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="h-screen">
      <AppLayout
        currentPage={currentPage}
        showFooter={true}
        showExtendedFooter={showExtendedFooter}
        user={user}
        onNavigate={handleNavigate}
        onUserMenuClick={() => alert('User menu clicked!')}
      >
        {renderPageContent()}
        
        {/* Demo Controls */}
        <div className="fixed bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg border z-50">
          <h4 className="font-semibold mb-2">Layout Demo Controls</h4>
          <div className="space-y-2">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={showExtendedFooter}
                onChange={(e) => setShowExtendedFooter(e.target.checked)}
              />
              <span className="text-sm">Extended Footer</span>
            </label>
          </div>
        </div>
      </AppLayout>
    </div>
  );
};

export default LayoutDemo;
