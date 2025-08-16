import React, { useState } from 'react';
import {
  User, Bell, Shield, Palette, Database, Key,
  Globe, Save, Eye, EyeOff, Moon, Sun
} from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';

interface SettingsSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
}

const settingsSections: SettingsSection[] = [
  {
    id: 'profile',
    title: 'Profile Settings',
    icon: <User className="h-5 w-5" />,
    description: 'Manage your personal information and preferences'
  },
  {
    id: 'notifications',
    title: 'Notifications',
    icon: <Bell className="h-5 w-5" />,
    description: 'Configure notification preferences and alerts'
  },
  {
    id: 'security',
    title: 'Security & Privacy',
    icon: <Shield className="h-5 w-5" />,
    description: 'Password, two-factor authentication, and privacy settings'
  },
  {
    id: 'appearance',
    title: 'Appearance',
    icon: <Palette className="h-5 w-5" />,
    description: 'Theme, language, and display preferences'
  },
  {
    id: 'integrations',
    title: 'Integrations',
    icon: <Database className="h-5 w-5" />,
    description: 'Manage external service connections and APIs'
  },
  {
    id: 'advanced',
    title: 'Advanced',
    icon: <Key className="h-5 w-5" />,
    description: 'Advanced system settings and configurations'
  }
];

export const SettingsPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('profile');
  const [showPassword, setShowPassword] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: false
  });

  const user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    role: 'admin'
  };

  const renderProfileSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
            <input
              type="text"
              defaultValue={user.name}
              className="julius-search-input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              defaultValue={user.email}
              className="julius-search-input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
            <input
              type="tel"
              placeholder="+84 123 456 789"
              className="julius-search-input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <input
              type="text"
              value={user.role}
              disabled
              className="julius-search-input bg-gray-50"
            />
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Picture</h3>
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-xl font-medium">
            {user.name.charAt(0)}
          </div>
          <div>
            <Button className="julius-btn julius-btn-secondary">
              Upload New Photo
            </Button>
            <p className="text-sm text-gray-500 mt-1">JPG, PNG up to 2MB</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">Email Notifications</h4>
              <p className="text-sm text-gray-500">Receive notifications via email</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.email}
                onChange={(e) => setNotifications(prev => ({ ...prev, email: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">Push Notifications</h4>
              <p className="text-sm text-gray-500">Receive push notifications in browser</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications.push}
                onChange={(e) => setNotifications(prev => ({ ...prev, push: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Password & Security</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                className="julius-search-input pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
            <input
              type="password"
              className="julius-search-input"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
            <input
              type="password"
              className="julius-search-input"
            />
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Two-Factor Authentication</h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            Two-factor authentication is not enabled. Enable it for better security.
          </p>
          <Button className="julius-btn julius-btn-primary mt-3">
            Enable 2FA
          </Button>
        </div>
      </div>
    </div>
  );

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Theme</h3>
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900">Dark Mode</h4>
            <p className="text-sm text-gray-500">Switch between light and dark themes</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={darkMode}
              onChange={(e) => setDarkMode(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Language</h3>
        <select className="julius-search-input">
          <option value="en">English</option>
          <option value="vi">Tiếng Việt</option>
          <option value="ja">日本語</option>
        </select>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'profile':
        return renderProfileSettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'security':
        return renderSecuritySettings();
      case 'appearance':
        return renderAppearanceSettings();
      case 'integrations':
        return (
          <div className="text-center py-12">
            <Database className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Integrations</h3>
            <p className="text-gray-600">Manage your external service connections</p>
          </div>
        );
      case 'advanced':
        return (
          <div className="text-center py-12">
            <Key className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Advanced Settings</h3>
            <p className="text-gray-600">Advanced system configurations</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
              <p className="text-gray-600 mt-1">Manage your account and application preferences</p>
            </div>
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            {/* Settings Navigation */}
            <div className="lg:w-1/4">
              <nav className="space-y-1">
                {settingsSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                      activeSection === section.id
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      {section.icon}
                      <div>
                        <div className="font-medium">{section.title}</div>
                        <div className="text-xs text-gray-500 hidden sm:block">
                          {section.description}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </nav>
            </div>

            {/* Settings Content */}
            <div className="lg:w-3/4">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                {renderContent()}
                
                <div className="flex justify-end space-x-3 mt-8 pt-6 border-t border-gray-200">
                  <Button variant="ghost" className="julius-btn julius-btn-secondary">
                    Cancel
                  </Button>
                  <Button className="julius-btn julius-btn-primary">
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  );
};

export default SettingsPage;
