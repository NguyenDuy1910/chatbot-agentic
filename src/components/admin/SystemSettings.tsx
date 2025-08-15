import React, { useState } from 'react';
import { SystemSettings } from '@/types/admin';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { 
  Settings, 
  Save, 
  Upload, 
  FileText, 
  Shield, 
  AlertTriangle,
  ToggleLeft,
  ToggleRight
} from 'lucide-react';

interface SystemSettingsProps {
  settings: SystemSettings;
  onUpdateSettings: (settings: Partial<SystemSettings>) => void;
}

export const SystemSettingsPanel: React.FC<SystemSettingsProps> = ({ 
  settings, 
  onUpdateSettings 
}) => {
  const [localSettings, setLocalSettings] = useState<SystemSettings>(settings);
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await onUpdateSettings(localSettings);
      // Show success message
    } catch (error) {
      console.error('Failed to update settings:', error);
      // Show error message
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const parseFileSize = (sizeStr: string): number => {
    const units: { [key: string]: number } = {
      'B': 1,
      'KB': 1024,
      'MB': 1024 * 1024,
      'GB': 1024 * 1024 * 1024
    };
    
    const match = sizeStr.match(/^(\d+(?:\.\d+)?)\s*(B|KB|MB|GB)$/i);
    if (!match) return 0;
    
    const value = parseFloat(match[1]);
    const unit = match[2].toUpperCase();
    return value * (units[unit] || 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Settings className="h-5 w-5 text-primary" />
          System Settings
        </h3>
        <Button 
          onClick={handleSave} 
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          <Save className="h-4 w-4" />
          {isLoading ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* File Upload Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-4 w-4 text-blue-500" />
              File Upload Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">Enable File Upload</label>
                <p className="text-xs text-muted-foreground">Allow users to upload files in chat</p>
              </div>
              <button
                onClick={() => setLocalSettings(prev => ({ 
                  ...prev, 
                  enableFileUpload: !prev.enableFileUpload 
                }))}
                className="flex items-center"
              >
                {localSettings.enableFileUpload ? (
                  <ToggleRight className="h-6 w-6 text-green-500" />
                ) : (
                  <ToggleLeft className="h-6 w-6 text-gray-400" />
                )}
              </button>
            </div>

            <div>
              <label className="text-sm font-medium text-foreground">Maximum File Size</label>
              <div className="flex items-center gap-2 mt-1">
                <Input
                  value={formatFileSize(localSettings.maxFileSize)}
                  onChange={(e) => {
                    const newSize = parseFileSize(e.target.value);
                    if (newSize > 0) {
                      setLocalSettings(prev => ({ ...prev, maxFileSize: newSize }));
                    }
                  }}
                  placeholder="10 MB"
                  className="w-32"
                />
                <span className="text-sm text-muted-foreground">per file</span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-foreground">Allowed File Types</label>
              <Textarea
                value={localSettings.allowedFileTypes.join(', ')}
                onChange={(e) => {
                  const types = e.target.value.split(',').map(t => t.trim()).filter(Boolean);
                  setLocalSettings(prev => ({ ...prev, allowedFileTypes: types }));
                }}
                placeholder="image/*, .pdf, .doc, .docx, .txt"
                className="mt-1 h-20"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Separate multiple types with commas
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Chat Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-green-500" />
              Chat Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">Enable Prompt Templates</label>
                <p className="text-xs text-muted-foreground">Allow users to use predefined prompts</p>
              </div>
              <button
                onClick={() => setLocalSettings(prev => ({ 
                  ...prev, 
                  enablePromptTemplates: !prev.enablePromptTemplates 
                }))}
                className="flex items-center"
              >
                {localSettings.enablePromptTemplates ? (
                  <ToggleRight className="h-6 w-6 text-green-500" />
                ) : (
                  <ToggleLeft className="h-6 w-6 text-gray-400" />
                )}
              </button>
            </div>

            <div>
              <label className="text-sm font-medium text-foreground">Max Chat History</label>
              <div className="flex items-center gap-2 mt-1">
                <Input
                  type="number"
                  value={localSettings.maxChatHistory}
                  onChange={(e) => setLocalSettings(prev => ({ 
                    ...prev, 
                    maxChatHistory: parseInt(e.target.value) || 0 
                  }))}
                  placeholder="100"
                  className="w-24"
                />
                <span className="text-sm text-muted-foreground">messages per session</span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-foreground">Rate Limit</label>
              <div className="flex items-center gap-2 mt-1">
                <Input
                  type="number"
                  value={localSettings.rateLimitPerMinute}
                  onChange={(e) => setLocalSettings(prev => ({ 
                    ...prev, 
                    rateLimitPerMinute: parseInt(e.target.value) || 0 
                  }))}
                  placeholder="60"
                  className="w-24"
                />
                <span className="text-sm text-muted-foreground">requests per minute</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-purple-500" />
              Security & Maintenance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-foreground">Maintenance Mode</label>
                <p className="text-xs text-muted-foreground">Temporarily disable the system</p>
              </div>
              <button
                onClick={() => setLocalSettings(prev => ({ 
                  ...prev, 
                  maintenanceMode: !prev.maintenanceMode 
                }))}
                className="flex items-center"
              >
                {localSettings.maintenanceMode ? (
                  <ToggleRight className="h-6 w-6 text-red-500" />
                ) : (
                  <ToggleLeft className="h-6 w-6 text-gray-400" />
                )}
              </button>
            </div>

            {localSettings.maintenanceMode && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <div className="flex items-center gap-2 text-red-800">
                  <AlertTriangle className="h-4 w-4" />
                  <span className="text-sm font-medium">Maintenance Mode Active</span>
                </div>
                <p className="text-xs text-red-700 mt-1">
                  The system is currently in maintenance mode. Users will see a maintenance page.
                </p>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">System Status</label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 bg-green-50 rounded border">
                  <div className="font-medium text-green-800">Database</div>
                  <div className="text-green-600">Healthy</div>
                </div>
                <div className="p-2 bg-green-50 rounded border">
                  <div className="font-medium text-green-800">API</div>
                  <div className="text-green-600">Online</div>
                </div>
                <div className="p-2 bg-blue-50 rounded border">
                  <div className="font-medium text-blue-800">Storage</div>
                  <div className="text-blue-600">75% Used</div>
                </div>
                <div className="p-2 bg-yellow-50 rounded border">
                  <div className="font-medium text-yellow-800">Queue</div>
                  <div className="text-yellow-600">23 Jobs</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Advanced Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              Advanced Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-3 bg-orange-50 border border-orange-200 rounded-md">
              <div className="flex items-center gap-2 text-orange-800">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm font-medium">Danger Zone</span>
              </div>
              <p className="text-xs text-orange-700 mt-1">
                These settings can affect system performance and user experience.
              </p>
            </div>

            <Button variant="outline" className="w-full justify-start text-orange-600 border-orange-200 hover:bg-orange-50">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Clear All User Sessions
            </Button>

            <Button variant="outline" className="w-full justify-start text-red-600 border-red-200 hover:bg-red-50">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Reset System to Defaults
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
