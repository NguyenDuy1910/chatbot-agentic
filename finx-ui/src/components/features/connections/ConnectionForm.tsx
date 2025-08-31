import React, { useState, useEffect } from 'react';
import { 
  Connection, 
  ConnectionFormData, 
  ConnectionType, 
  AuthenticationType,
  ConnectionTemplate,
  ConnectionTestResult
} from '@/types/features/connections';
import { Button } from '@/components/shared/ui/Button';
import { Input } from '@/components/shared/ui/Input';
import { Select } from '@/components/shared/ui/Select';
import { Textarea } from '@/components/shared/ui/Textarea';
import { Card } from '@/components/shared/ui/Card';
import { 
  X, 
  TestTube, 
  Eye, 
  EyeOff, 
  Loader2, 
  CheckCircle, 
  AlertCircle,
  Info,
  Plus,
  Trash2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { connectionAPI } from '@/lib/connectionAPI';

interface ConnectionFormProps {
  connection?: Connection;
  template?: ConnectionTemplate;
  onSave: (connectionData: ConnectionFormData) => Promise<void>;
  onCancel: () => void;
  onTest?: (connectionData: ConnectionFormData) => Promise<ConnectionTestResult>;
  isLoading?: boolean;
}

export const ConnectionForm: React.FC<ConnectionFormProps> = ({
  connection,
  template,
  onSave,
  onCancel,
  onTest,
  isLoading = false
}) => {
  const [formData, setFormData] = useState<ConnectionFormData>({
    name: connection?.name || template?.name || '',
    description: connection?.description || template?.description || '',
    type: connection?.type || template?.type || 'api',
    provider: connection?.provider || template?.provider || '',
    config: {
      baseUrl: connection?.config.baseUrl || '',
      timeout: connection?.config.timeout || 30,
      retryAttempts: connection?.config.retryAttempts || 3,
      retryDelay: connection?.config.retryDelay || 1,
      customSettings: connection?.config.customSettings || {}
    },
    credentials: {
      type: connection?.credentials.type || 'api_key',
      apiKey: connection?.credentials.apiKey || '',
      bearerToken: connection?.credentials.bearerToken || '',
      username: connection?.credentials.username || '',
      password: connection?.credentials.password || '',
      clientId: connection?.credentials.clientId || '',
      clientSecret: connection?.credentials.clientSecret || '',
      customHeaders: connection?.credentials.customHeaders || {}
    },
    healthCheck: {
      enabled: connection?.healthCheck.enabled ?? true,
      interval: connection?.healthCheck.interval || 5,
      endpoint: connection?.healthCheck.endpoint || '',
      method: connection?.healthCheck.method || 'GET',
      expectedStatus: connection?.healthCheck.expectedStatus || 200,
      timeout: connection?.healthCheck.timeout || 10
    },
    tags: connection?.tags || [],
    category: connection?.category || template?.category || '',
    isActive: connection?.isActive ?? true
  });

  const [showPassword, setShowPassword] = useState(false);
  const [testResult, setTestResult] = useState<ConnectionTestResult | null>(null);
  const [testing, setTesting] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [customHeaderKey, setCustomHeaderKey] = useState('');
  const [customHeaderValue, setCustomHeaderValue] = useState('');

  // Apply template defaults when template changes
  useEffect(() => {
    if (template && !connection) {
      setFormData(prev => ({
        ...prev,
        name: template.name,
        description: template.description,
        type: template.type,
        provider: template.provider,
        category: template.category,
        config: {
          ...prev.config,
          ...(template.defaultConfig || {})
        },
        healthCheck: {
          ...prev.healthCheck,
          ...(template.defaultHealthCheck || {})
        }
      }));
    }
  }, [template, connection]);

  const connectionTypes: { value: ConnectionType; label: string }[] = [
    { value: 'api', label: 'API' },
    { value: 'database', label: 'Database' },
    { value: 'webhook', label: 'Webhook' },
    { value: 'oauth', label: 'OAuth' },
    { value: 'file_storage', label: 'File Storage' },
    { value: 'messaging', label: 'Messaging' },
    { value: 'analytics', label: 'Analytics' },
    { value: 'payment', label: 'Payment' },
    { value: 'email', label: 'Email' },
    { value: 'sms', label: 'SMS' },
    { value: 'social_media', label: 'Social Media' },
    { value: 'crm', label: 'CRM' },
    { value: 'erp', label: 'ERP' },
    { value: 'custom', label: 'Custom' }
  ];

  const authTypes: { value: AuthenticationType; label: string }[] = [
    { value: 'none', label: 'None' },
    { value: 'api_key', label: 'API Key' },
    { value: 'bearer_token', label: 'Bearer Token' },
    { value: 'basic_auth', label: 'Basic Auth' },
    { value: 'oauth2', label: 'OAuth 2.0' },
    { value: 'oauth1', label: 'OAuth 1.0' },
    { value: 'custom_header', label: 'Custom Header' },
    { value: 'certificate', label: 'Certificate' },
    { value: 'jwt', label: 'JWT' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim() && formData.provider.trim()) {
      await onSave(formData);
    }
  };

  const handleTest = async () => {
    if (!onTest) return;
    
    setTesting(true);
    setTestResult(null);
    
    try {
      const result = await onTest(formData);
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Test failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date()
      });
    } finally {
      setTesting(false);
    }
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove) || []
    }));
  };

  const addCustomHeader = () => {
    if (customHeaderKey.trim() && customHeaderValue.trim()) {
      setFormData(prev => ({
        ...prev,
        credentials: {
          ...prev.credentials,
          customHeaders: {
            ...prev.credentials.customHeaders,
            [customHeaderKey.trim()]: customHeaderValue.trim()
          }
        }
      }));
      setCustomHeaderKey('');
      setCustomHeaderValue('');
    }
  };

  const removeCustomHeader = (key: string) => {
    setFormData(prev => {
      const newHeaders = { ...prev.credentials.customHeaders };
      delete newHeaders[key];
      return {
        ...prev,
        credentials: {
          ...prev.credentials,
          customHeaders: newHeaders
        }
      };
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {connection ? 'Edit Connection' : 'New Connection'}
          </h2>
          <p className="text-gray-600 mt-1">
            {template ? `Create a new ${template.name} connection` : 'Configure your external service connection'}
          </p>
        </div>
        <Button variant="ghost" onClick={onCancel}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {template && template.setupInstructions && (
        <Card className="p-4 mb-6 bg-blue-50 border-blue-200">
          <div className="flex items-start space-x-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-medium text-blue-900 mb-2">Setup Instructions</h3>
              <div className="text-sm text-blue-800 whitespace-pre-line">
                {template.setupInstructions}
              </div>
            </div>
          </div>
        </Card>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Connection Name *
              </label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="My API Connection"
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                Provider *
              </label>
              <Input
                value={formData.provider}
                onChange={(e) => setFormData(prev => ({ ...prev, provider: e.target.value }))}
                placeholder="stripe, slack, custom"
                required
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="text-sm font-medium mb-2 block">
              Description
            </label>
            <Textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe what this connection is used for..."
              rows={3}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Connection Type *
              </label>
              <Select
                value={formData.type}
                onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as ConnectionType }))}
              >
                {connectionTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                Category
              </label>
              <Input
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                placeholder="Payment, Communication, etc."
              />
            </div>
          </div>

          {/* Tags */}
          <div className="mt-4">
            <label className="text-sm font-medium mb-2 block">
              Tags
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.tags?.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => removeTag(tag)}
                    className="ml-1 text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex space-x-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag..."
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              />
              <Button type="button" onClick={addTag} variant="outline" size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Configuration */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Configuration</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Base URL
              </label>
              <Input
                value={formData.config.baseUrl}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  config: { ...prev.config, baseUrl: e.target.value }
                }))}
                placeholder="https://api.example.com"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                Timeout (seconds)
              </label>
              <Input
                type="number"
                value={formData.config.timeout}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  config: { ...prev.config, timeout: parseInt(e.target.value) || 30 }
                }))}
                min="1"
                max="300"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                Retry Attempts
              </label>
              <Input
                type="number"
                value={formData.config.retryAttempts}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  config: { ...prev.config, retryAttempts: parseInt(e.target.value) || 3 }
                }))}
                min="0"
                max="10"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">
                Retry Delay (seconds)
              </label>
              <Input
                type="number"
                value={formData.config.retryDelay}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  config: { ...prev.config, retryDelay: parseInt(e.target.value) || 1 }
                }))}
                min="0"
                max="60"
              />
            </div>
          </div>
        </Card>

        {/* Authentication */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Authentication</h3>
          
          <div className="mb-4">
            <label className="text-sm font-medium mb-2 block">
              Authentication Type
            </label>
            <Select
              value={formData.credentials.type}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                credentials: { ...prev.credentials, type: e.target.value as AuthenticationType }
              }))}
            >
              {authTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </Select>
          </div>

          {/* Conditional credential fields based on auth type */}
          {formData.credentials.type === 'api_key' && (
            <div>
              <label className="text-sm font-medium mb-2 block">
                API Key
              </label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.credentials.apiKey}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    credentials: { ...prev.credentials, apiKey: e.target.value }
                  }))}
                  placeholder="Enter your API key"
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
          )}

          {formData.credentials.type === 'bearer_token' && (
            <div>
              <label className="text-sm font-medium mb-2 block">
                Bearer Token
              </label>
              <div className="relative">
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.credentials.bearerToken}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    credentials: { ...prev.credentials, bearerToken: e.target.value }
                  }))}
                  placeholder="Enter your bearer token"
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
          )}

          {formData.credentials.type === 'basic_auth' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Username
                </label>
                <Input
                  value={formData.credentials.username}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    credentials: { ...prev.credentials, username: e.target.value }
                  }))}
                  placeholder="Username"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Password
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.credentials.password}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      credentials: { ...prev.credentials, password: e.target.value }
                    }))}
                    placeholder="Password"
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
            </div>
          )}

          {(formData.credentials.type === 'oauth2' || formData.credentials.type === 'oauth1') && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Client ID
                </label>
                <Input
                  value={formData.credentials.clientId}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    credentials: { ...prev.credentials, clientId: e.target.value }
                  }))}
                  placeholder="Client ID"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Client Secret
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.credentials.clientSecret}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      credentials: { ...prev.credentials, clientSecret: e.target.value }
                    }))}
                    placeholder="Client Secret"
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
            </div>
          )}

          {/* Custom Headers */}
          {(formData.credentials.type === 'custom_header' || Object.keys(formData.credentials.customHeaders || {}).length > 0) && (
            <div className="mt-4">
              <label className="text-sm font-medium mb-2 block">
                Custom Headers
              </label>
              
              {/* Existing headers */}
              {Object.entries(formData.credentials.customHeaders || {}).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2 mb-2">
                  <Input value={key} disabled className="flex-1" />
                  <Input value={value} disabled className="flex-1" />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => removeCustomHeader(key)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              
              {/* Add new header */}
              <div className="flex items-center space-x-2">
                <Input
                  value={customHeaderKey}
                  onChange={(e) => setCustomHeaderKey(e.target.value)}
                  placeholder="Header name"
                  className="flex-1"
                />
                <Input
                  value={customHeaderValue}
                  onChange={(e) => setCustomHeaderValue(e.target.value)}
                  placeholder="Header value"
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addCustomHeader}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* Health Check */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Health Check</h3>
          
          <div className="flex items-center space-x-2 mb-4">
            <input
              type="checkbox"
              id="healthCheckEnabled"
              checked={formData.healthCheck.enabled}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                healthCheck: { ...prev.healthCheck, enabled: e.target.checked }
              }))}
              className="rounded border-gray-300"
            />
            <label htmlFor="healthCheckEnabled" className="text-sm font-medium">
              Enable health checks
            </label>
          </div>

          {formData.healthCheck.enabled && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Check Interval (minutes)
                </label>
                <Input
                  type="number"
                  value={formData.healthCheck.interval}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    healthCheck: { ...prev.healthCheck, interval: parseInt(e.target.value) || 5 }
                  }))}
                  min="1"
                  max="1440"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Health Check Endpoint
                </label>
                <Input
                  value={formData.healthCheck.endpoint}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    healthCheck: { ...prev.healthCheck, endpoint: e.target.value }
                  }))}
                  placeholder="/health or leave empty for base URL"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Expected Status Code
                </label>
                <Input
                  type="number"
                  value={formData.healthCheck.expectedStatus}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    healthCheck: { ...prev.healthCheck, expectedStatus: parseInt(e.target.value) || 200 }
                  }))}
                  min="100"
                  max="599"
                />
              </div>
            </div>
          )}
        </Card>

        {/* Test Result */}
        {testResult && (
          <Card className={cn(
            "p-4",
            testResult.success 
              ? "bg-green-50 border-green-200" 
              : "bg-red-50 border-red-200"
          )}>
            <div className="flex items-center space-x-2">
              {testResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600" />
              )}
              <span className={cn(
                "font-medium",
                testResult.success ? "text-green-800" : "text-red-800"
              )}>
                {testResult.message}
              </span>
            </div>
            {testResult.responseTime && (
              <p className={cn(
                "mt-1 text-sm",
                testResult.success ? "text-green-700" : "text-red-700"
              )}>
                Response time: {Math.round(testResult.responseTime * 1000)}ms
              </p>
            )}
            {testResult.error && (
              <p className={cn(
                "mt-1 text-sm",
                testResult.success ? "text-green-700" : "text-red-700"
              )}>
                {testResult.error}
              </p>
            )}
          </Card>
        )}

        {/* Form Actions */}
        <div className="flex items-center justify-between pt-6 border-t">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="isActive"
              checked={formData.isActive}
              onChange={(e) => setFormData(prev => ({ ...prev, isActive: e.target.checked }))}
              className="rounded border-gray-300"
            />
            <label htmlFor="isActive" className="text-sm font-medium">
              Active connection
            </label>
          </div>

          <div className="flex items-center space-x-3">
            {onTest && (
              <Button
                type="button"
                variant="outline"
                onClick={handleTest}
                disabled={testing || isLoading}
              >
                {testing ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <TestTube className="h-4 w-4 mr-2" />
                )}
                Test Connection
              </Button>
            )}
            
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isLoading}
            >
              Cancel
            </Button>
            
            <Button
              type="submit"
              disabled={isLoading || !formData.name.trim() || !formData.provider.trim()}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : null}
              {connection ? 'Update' : 'Create'} Connection
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};
