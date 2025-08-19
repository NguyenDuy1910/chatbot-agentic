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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                File Management
              </h1>
              <p className="text-default-600 mt-2 text-lg">Upload, organize, and manage your data files with ease</p>
            </div>
            <Button 
              color="primary" 
              size="lg"
              startContent={<Plus className="h-5 w-5" />}
              onPress={onUploadOpen}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
            >
              Upload Files
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg">
                    <File className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Total Files</p>
                    <p className="text-2xl font-bold text-foreground">{files.length}</p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg">
                    <FileText className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Documents</p>
                    <p className="text-2xl font-bold text-foreground">
                      {files.filter(f => f.type === 'document').length}
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-pink-500 to-rose-600 text-white shadow-lg">
                    <Image className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Images</p>
                    <p className="text-2xl font-bold text-foreground">
                      {files.filter(f => f.type === 'image').length}
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card className="group hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:scale-[1.02]">
              <CardBody className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 text-white shadow-lg">
                    <Archive className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm text-default-500 font-medium">Archives</p>
                    <p className="text-2xl font-bold text-foreground">
                      {files.filter(f => f.type === 'archive').length}
                    </p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>

          {/* Search and Filters */}
          <Card className="mb-8 bg-white/70 backdrop-blur-sm border-0 shadow-lg">
            <CardBody className="p-6">
              <div className="flex flex-col lg:flex-row gap-6">
                <div className="flex-1">
                  <Input
                    placeholder="Search files..."
                    value={searchTerm}
                    onValueChange={setSearchTerm}
                    startContent={<Search className="h-4 w-4 text-default-400" />}
                    variant="bordered"
                    size="lg"
                    classNames={{
                      input: "text-sm",
                      inputWrapper: "bg-white/50 border-default-200 hover:border-primary-300 focus-within:border-primary-500"
                    }}
                  />
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="flex-shrink-0">
                    <Tabs
                      selectedKey={selectedType}
                      onSelectionChange={(key) => setSelectedType(key as string)}
                      variant="bordered"
                      color="primary"
                      classNames={{
                        tabList: "bg-white/50 backdrop-blur-sm",
                        tab: "data-[selected=true]:bg-primary-500 data-[selected=true]:text-white",
                      }}
                    >
                      {fileTypes.map(type => (
                        <Tab 
                          key={type} 
                          title={type.charAt(0).toUpperCase() + type.slice(1)}
                        />
                      ))}
                    </Tabs>
                  </div>

                  <div className="flex items-center gap-1 border-l border-divider pl-4">
                    <Button
                      isIconOnly
                      size="sm"
                      variant={viewMode === 'grid' ? 'solid' : 'light'}
                      color={viewMode === 'grid' ? 'primary' : 'default'}
                      onPress={() => setViewMode('grid')}
                      className="transition-all duration-200"
                    >
                      <Grid3X3 className="h-4 w-4" />
                    </Button>
                    <Button
                      isIconOnly
                      size="sm"
                      variant={viewMode === 'list' ? 'solid' : 'light'}
                      color={viewMode === 'list' ? 'primary' : 'default'}
                      onPress={() => setViewMode('list')}
                      className="transition-all duration-200"
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
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
              <CardBody className="p-12 text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500/10 to-purple-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <File className="h-10 w-10 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2 text-foreground">No files found</h3>
                <p className="text-default-600 mb-6 max-w-md mx-auto">
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
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  Upload Files
                </Button>
              </CardBody>
            </Card>
          )}
        </div>
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
