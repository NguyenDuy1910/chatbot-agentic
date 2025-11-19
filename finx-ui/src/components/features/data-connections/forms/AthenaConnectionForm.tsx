import React, { useState } from 'react';
import { Button, Input, Card, CardBody, Select, SelectItem, Alert, Checkbox } from '@heroui/react';
import { AlertCircle, CheckCircle, Loader2, Info } from 'lucide-react';
import { createAthenaClient, type AthenaConnectionConfig } from '@/lib/athenaClient';

export interface AthenaConnectionFormProps {
  onSuccess?: (connectionConfig: AthenaConnectionConfig) => void;
  onCancel?: () => void;
}

export const AthenaConnectionForm: React.FC<AthenaConnectionFormProps> = ({
  onSuccess,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    region: 'us-east-1',
    workgroup: 'primary',
    s3OutputLocation: '',
    database: '',
    useEnvironmentAuth: false, // Default to false in browser
    accessKeyId: '',
    secretAccessKey: '',
    sessionToken: '', // Optional for temporary credentials
    catalogType: 'glue' as 'glue' | 's3tables',
    tableBucketArn: '', // For S3 Tables
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<any>(null);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('Connection name is required');
      return false;
    }
    if (!formData.s3OutputLocation.trim()) {
      setError('S3 Output Location is required');
      return false;
    }
    // Check table bucket ARN for S3 Tables
    if (formData.catalogType === 's3tables' && !formData.tableBucketArn.trim()) {
      setError('Table Bucket ARN is required for S3 Tables catalog');
      return false;
    }
    // In browser, credentials are always required
    if (!formData.accessKeyId.trim()) {
      setError('AWS Access Key ID is required');
      return false;
    }
    if (!formData.secretAccessKey.trim()) {
      setError('AWS Secret Access Key is required');
      return false;
    }
    return true;
  };

  const handleTestConnection = async () => {
    if (!validateForm()) return;

    setIsTesting(true);
    setError(null);
    setSuccess(null);
    setTestResult(null);
    
    try {
      // Create Athena client with form data
      const athenaConfig: AthenaConnectionConfig = {
        region: formData.region,
        workgroup: formData.workgroup,
        s3OutputLocation: formData.s3OutputLocation,
        database: formData.database,
        useEnvironmentAuth: formData.useEnvironmentAuth,
        accessKeyId: formData.accessKeyId,
        secretAccessKey: formData.secretAccessKey,
        sessionToken: formData.sessionToken || undefined,
        catalogType: formData.catalogType,
        tableBucketArn: formData.tableBucketArn || undefined,
      };

      const client = createAthenaClient(athenaConfig);
      const result = await client.testConnection();

      setTestResult(result);
      if (result.success) {
        setSuccess(result.message);
      } else {
        setError(result.error || 'Connection test failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to test connection');
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      // Create Athena connection config
      const athenaConfig: AthenaConnectionConfig = {
        region: formData.region,
        workgroup: formData.workgroup,
        s3OutputLocation: formData.s3OutputLocation,
        database: formData.database,
        useEnvironmentAuth: formData.useEnvironmentAuth,
        accessKeyId: formData.accessKeyId,
        secretAccessKey: formData.secretAccessKey,
        sessionToken: formData.sessionToken || undefined,
        catalogType: formData.catalogType,
        tableBucketArn: formData.tableBucketArn || undefined,
      };

      // Test connection before saving
      const client = createAthenaClient(athenaConfig);
      const testResult = await client.testConnection();
      
      if (!testResult.success) {
        setError(testResult.error || 'Connection test failed. Please check your credentials.');
        setIsLoading(false);
        return;
      }

      setSuccess('Athena connection created successfully!');
      
      // Pass the config to parent component
      setTimeout(() => {
        onSuccess?.(athenaConfig);
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create connection');
    } finally {
      setIsLoading(false);
    }
  };

  const awsRegions = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'eu-west-1',
    'eu-central-1',
    'ap-southeast-1',
    'ap-southeast-5', // Malaysia (Kuala Lumpur)
    'ap-northeast-1',
  ];

  return (
    <Card className="w-full">
      <CardBody className="gap-4">
        <h3 className="text-lg font-semibold">Create Amazon Athena Connection</h3>

        <Alert
          color="primary"
          startContent={<Info className="h-4 w-4" />}
          title="Browser Authentication"
          description="In browser environment, you must provide AWS credentials directly. Environment variables are not accessible from the browser."
        />

        {error && (
          <Alert
            color="danger"
            startContent={<AlertCircle className="h-4 w-4" />}
            title="Error"
            description={error}
          />
        )}

        {success && (
          <Alert
            color="success"
            startContent={<CheckCircle className="h-4 w-4" />}
            title="Success"
            description={success}
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Connection Name"
            placeholder="e.g., My Athena Connection"
            value={formData.name}
            onChange={e => handleInputChange('name', e.target.value)}
            isRequired
          />

          <Input
            label="Description"
            placeholder="Optional description"
            value={formData.description}
            onChange={e => handleInputChange('description', e.target.value)}
          />

          <Select
            label="AWS Region"
            selectedKeys={[formData.region]}
            onChange={e => handleInputChange('region', e.target.value)}
          >
            {awsRegions.map(region => (
              <SelectItem key={region}>
                {region}
              </SelectItem>
            ))}
          </Select>

          <Select
            label="Catalog Type"
            selectedKeys={[formData.catalogType]}
            onChange={e => handleInputChange('catalogType', e.target.value)}
            description="Select AWS Glue Data Catalog or S3 Tables"
          >
            <SelectItem key="glue">AWS Glue Data Catalog</SelectItem>
            <SelectItem key="s3tables">S3 Tables (Iceberg)</SelectItem>
          </Select>

          {formData.catalogType === 's3tables' && (
            <Input
              label="Table Bucket ARN"
              placeholder="arn:aws:s3tables:region:account-id:bucket/bucket-name"
              value={formData.tableBucketArn}
              onChange={e => handleInputChange('tableBucketArn', e.target.value)}
              description="Required for S3 Tables catalog"
              isRequired
            />
          )}

          <Input
            label="Workgroup"
            placeholder="primary"
            value={formData.workgroup}
            onChange={e => handleInputChange('workgroup', e.target.value)}
          />

          <Input
            label="S3 Output Location"
            placeholder="s3://my-bucket/athena-results/"
            value={formData.s3OutputLocation}
            onChange={e => handleInputChange('s3OutputLocation', e.target.value)}
            isRequired
          />

          <Input
            label="Database (Optional)"
            placeholder="default"
            value={formData.database}
            onChange={e => handleInputChange('database', e.target.value)}
          />

          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-semibold text-gray-700">AWS Credentials (Required)</p>
            <Input
              label="AWS Access Key ID"
              placeholder="AKIA..."
              value={formData.accessKeyId}
              onChange={e => handleInputChange('accessKeyId', e.target.value)}
              isRequired
            />

            <Input
              label="AWS Secret Access Key"
              type="password"
              placeholder="••••••••"
              value={formData.secretAccessKey}
              onChange={e => handleInputChange('secretAccessKey', e.target.value)}
              isRequired
            />

            <Input
              label="Session Token (Optional)"
              type="password"
              placeholder="For temporary credentials only"
              description="Only required if using temporary/STS credentials"
              value={formData.sessionToken}
              onChange={e => handleInputChange('sessionToken', e.target.value)}
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              color="primary"
              variant="bordered"
              onClick={handleTestConnection}
              isLoading={isTesting}
            >
              Test Connection
            </Button>

            <Button
              color="primary"
              type="submit"
              isLoading={isLoading}
            >
              Create Connection
            </Button>

            {onCancel && (
              <Button color="default" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>
        </form>

        {testResult && (
          <Card className="bg-gray-50">
            <CardBody className="text-sm">
              <p className="font-semibold">Test Result:</p>
              <p>{testResult.message}</p>
            </CardBody>
          </Card>
        )}
      </CardBody>
    </Card>
  );
};

export default AthenaConnectionForm;

