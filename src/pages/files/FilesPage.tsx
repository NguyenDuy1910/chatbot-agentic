import React, { useState } from 'react';
import {
  Button,
  Input,
  Card,
  CardBody,
  Chip,
  Tabs,
  Tab,
  useDisclosure,
  Spinner,
} from '@heroui/react';
import {
  Upload,
  Search,
  File,
  FileText,
  Image,
  Archive,
  Filter,
  Grid3X3,
  List,
  Plus,
} from 'lucide-react';
import { FileUploadModal, FileCard, FileListItem } from '@/components/features/files';

interface FileItem {
  id: string;
  name: string;
  type: 'document' | 'image' | 'archive' | 'other';
  size: number;
  uploadDate: Date;
  lastAccessed: Date;
  status: 'processing' | 'ready' | 'error';
}

const mockFiles: FileItem[] = [
  {
    id: '1',
    name: 'sales_data_q4_2023.csv',
    type: 'document',
    size: 2048576, // 2MB
    uploadDate: new Date('2024-01-15'),
    lastAccessed: new Date('2024-01-16'),
    status: 'ready'
  },
  {
    id: '2',
    name: 'customer_analysis_report.pdf',
    type: 'document',
    size: 5242880, // 5MB
    uploadDate: new Date('2024-01-14'),
    lastAccessed: new Date('2024-01-15'),
    status: 'ready'
  },
  {
    id: '3',
    name: 'product_images.zip',
    type: 'archive',
    size: 15728640, // 15MB
    uploadDate: new Date('2024-01-13'),
    lastAccessed: new Date('2024-01-14'),
    status: 'processing'
  },
  {
    id: '4',
    name: 'dashboard_screenshot.png',
    type: 'image',
    size: 1048576, // 1MB
    uploadDate: new Date('2024-01-12'),
    lastAccessed: new Date('2024-01-13'),
    status: 'ready'
  },
  {
    id: '5',
    name: 'financial_model.xlsx',
    type: 'document',
    size: 3145728, // 3MB
    uploadDate: new Date('2024-01-11'),
    lastAccessed: new Date('2024-01-12'),
    status: 'error'
  }
];

export const FilesPage: React.FC = () => {
  const [files, setFiles] = useState<FileItem[]>(mockFiles);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(false);
  const { isOpen: isUploadOpen, onOpen: onUploadOpen, onClose: onUploadClose } = useDisclosure();

  const user = {
    name: 'Nguyễn Đình Quốc Duy',
    email: 'nguyendinhduy@gmail.com',
    role: 'admin'
  };

  const fileTypes = ['all', 'document', 'image', 'archive', 'other'];

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || file.type === selectedType;
    return matchesSearch && matchesType;
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };



  const handleUploadComplete = (uploadedFiles: File[]) => {
    // Convert uploaded files to FileItem format
    const newFiles: FileItem[] = uploadedFiles.map(file => ({
      id: Math.random().toString(36).substring(2, 11),
      name: file.name,
      type: getFileType(file.type),
      size: file.size,
      uploadDate: new Date(),
      lastAccessed: new Date(),
      status: 'ready',
    }));

    setFiles(prev => [...newFiles, ...prev]);
  };

  const getFileType = (mimeType: string): 'document' | 'image' | 'archive' | 'other' => {
    if (mimeType.startsWith('image/')) return 'image';
    if (mimeType.includes('text') || mimeType.includes('document') || mimeType.includes('pdf')) return 'document';
    if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('archive')) return 'archive';
    return 'other';
  };

  const handleDelete = (id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  };

  const handleRename = (id: string, newName: string) => {
    setFiles(prev => prev.map(file =>
      file.id === id ? { ...file, name: newName } : file
    ));
  };

  const handleDownload = (id: string) => {
    const file = files.find(f => f.id === id);
    if (file) {
      console.log('Downloading file:', file.name);
      // Implement download logic here
    }
  };

  const handleView = (id: string) => {
    const file = files.find(f => f.id === id);
    if (file) {
      console.log('Viewing file:', file.name);
      // Implement view logic here
      setFiles(prev => prev.map(f =>
        f.id === id ? { ...f, lastAccessed: new Date() } : f
      ));
    }
  };

  return (
    <div className="h-full bg-gradient-to-br from-background via-background to-default-50/50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              File Management
            </h1>
            <p className="text-default-600 mt-2">
              Upload, organize, and manage your data files with ease
            </p>
          </div>
          <Button
            color="primary"
            size="lg"
            startContent={<Plus className="h-5 w-5" />}
            onPress={onUploadOpen}
            className="shadow-lg"
          >
            Upload Files
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="shadow-sm">
            <CardBody className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <File className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-default-500">Total Files</p>
                  <p className="text-xl font-semibold">{files.length}</p>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card className="shadow-sm">
            <CardBody className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-success/10">
                  <FileText className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-sm text-default-500">Documents</p>
                  <p className="text-xl font-semibold">
                    {files.filter(f => f.type === 'document').length}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card className="shadow-sm">
            <CardBody className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-secondary/10">
                  <Image className="h-5 w-5 text-secondary" />
                </div>
                <div>
                  <p className="text-sm text-default-500">Images</p>
                  <p className="text-xl font-semibold">
                    {files.filter(f => f.type === 'image').length}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card className="shadow-sm">
            <CardBody className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-warning/10">
                  <Archive className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <p className="text-sm text-default-500">Archives</p>
                  <p className="text-xl font-semibold">
                    {files.filter(f => f.type === 'archive').length}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Search and Filters */}
        <Card className="shadow-sm mb-6">
          <CardBody className="p-4">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <Input
                  placeholder="Search files..."
                  value={searchTerm}
                  onValueChange={setSearchTerm}
                  startContent={<Search className="h-4 w-4 text-default-400" />}
                  variant="bordered"
                  classNames={{
                    input: "text-sm",
                    inputWrapper: "h-10"
                  }}
                />
              </div>

              {/* Filters */}
              <div className="flex items-center gap-3">
                <Tabs
                  selectedKey={selectedType}
                  onSelectionChange={(key) => setSelectedType(key as string)}
                  variant="bordered"
                  size="sm"
                >
                  {fileTypes.map(type => (
                    <Tab key={type} title={type.charAt(0).toUpperCase() + type.slice(1)} />
                  ))}
                </Tabs>

                <div className="flex items-center gap-1 border-l border-divider pl-3">
                  <Button
                    isIconOnly
                    size="sm"
                    variant={viewMode === 'grid' ? 'solid' : 'light'}
                    color={viewMode === 'grid' ? 'primary' : 'default'}
                    onPress={() => setViewMode('grid')}
                  >
                    <Grid3X3 className="h-4 w-4" />
                  </Button>
                  <Button
                    isIconOnly
                    size="sm"
                    variant={viewMode === 'list' ? 'solid' : 'light'}
                    color={viewMode === 'list' ? 'primary' : 'default'}
                    onPress={() => setViewMode('list')}
                  >
                    <List className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Files Display */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Spinner size="lg" color="primary" />
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredFiles.map((file) => (
              <FileCard
                key={file.id}
                file={file}
                onDelete={handleDelete}
                onRename={handleRename}
                onDownload={handleDownload}
                onView={handleView}
              />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredFiles.map((file) => (
              <FileListItem
                key={file.id}
                file={file}
                onDelete={handleDelete}
                onRename={handleRename}
                onDownload={handleDownload}
                onView={handleView}
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {filteredFiles.length === 0 && !isLoading && (
          <Card className="shadow-sm">
            <CardBody className="p-12 text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <File className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No files found</h3>
              <p className="text-default-500 mb-6 max-w-md mx-auto">
                {searchTerm || selectedType !== 'all'
                  ? 'Try adjusting your search criteria or filters to find what you\'re looking for.'
                  : 'Get started by uploading your first file. We support various formats including documents, images, and archives.'
                }
              </p>
              <Button
                color="primary"
                size="lg"
                startContent={<Upload className="h-5 w-5" />}
                onPress={onUploadOpen}
              >
                Upload Files
              </Button>
            </CardBody>
          </Card>
        )}
      </div>

      {/* Upload Modal */}
      <FileUploadModal
        isOpen={isUploadOpen}
        onClose={onUploadClose}
        onUploadComplete={handleUploadComplete}
      />
    </div>
  );
};

export default FilesPage;
