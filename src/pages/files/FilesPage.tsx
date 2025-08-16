import React, { useState } from 'react';
import { Upload, Search, File, FileText, Image, Archive, Download, Trash2, Eye, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/shared/ui/Button';

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
  const [dragOver, setDragOver] = useState(false);

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

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'document':
        return <FileText className="h-8 w-8 text-blue-600" />;
      case 'image':
        return <Image className="h-8 w-8 text-green-600" />;
      case 'archive':
        return <Archive className="h-8 w-8 text-purple-600" />;
      default:
        return <File className="h-8 w-8 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      ready: 'julius-badge julius-badge-green',
      processing: 'julius-badge julius-badge-yellow',
      error: 'julius-badge julius-badge-red'
    };
    return statusStyles[status as keyof typeof statusStyles] || 'julius-badge julius-badge-gray';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    // Handle file drop logic here
    console.log('Files dropped:', e.dataTransfer.files);
  };

  const handleDelete = (id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  };

  return (
    <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Files</h1>
              <p className="text-gray-600 mt-1">Upload and manage your data files</p>
            </div>
            <Button className="julius-btn julius-btn-primary">
              <Upload className="h-4 w-4 mr-2" />
              Upload Files
            </Button>
          </div>

          {/* Upload Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 mb-6 text-center transition-colors ${
              dragOver 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Drop files here or click to upload
            </h3>
            <p className="text-gray-600 mb-4">
              Support for CSV, Excel, PDF, images and more
            </p>
            <Button className="julius-btn julius-btn-secondary">
              Choose Files
            </Button>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1 julius-search-container">
              <Search className="julius-search-icon" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="julius-search-input"
              />
            </div>
            <div className="flex gap-2">
              {fileTypes.map(type => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedType === type
                      ? 'bg-blue-100 text-blue-700 border border-blue-200'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Files Grid */}
          <div className="julius-grid">
            {filteredFiles.map((file) => (
              <div key={file.id} className="julius-template-card">
                <div className="flex items-start justify-between mb-4">
                  <div className="julius-template-icon">
                    {getFileIcon(file.type)}
                  </div>
                  <button className="p-1 rounded text-gray-400 hover:text-gray-600">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>

                <div className="mb-4">
                  <h3 className="julius-template-title truncate" title={file.name}>
                    {file.name}
                  </h3>
                  <p className="julius-template-description">
                    Size: {formatFileSize(file.size)}
                  </p>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="julius-badge julius-badge-blue">
                      {file.type.charAt(0).toUpperCase() + file.type.slice(1)}
                    </span>
                    <span className={getStatusBadge(file.status)}>
                      {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                    </span>
                  </div>
                </div>

                <div className="text-xs text-gray-500 mb-4">
                  <div>Uploaded: {file.uploadDate.toLocaleDateString()}</div>
                  <div>Last accessed: {file.lastAccessed.toLocaleDateString()}</div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button size="sm" className="julius-btn julius-btn-primary flex-1">
                    <Eye className="h-3 w-3 mr-1" />
                    View
                  </Button>
                  <Button size="sm" variant="ghost" className="p-2">
                    <Download className="h-3 w-3" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    className="p-2 text-red-600 hover:text-red-700"
                    onClick={() => handleDelete(file.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {filteredFiles.length === 0 && (
            <div className="text-center py-12">
              <File className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No files found</h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || selectedType !== 'all' 
                  ? 'Try adjusting your search or filters'
                  : 'Upload your first file to get started'
                }
              </p>
              <Button className="julius-btn julius-btn-primary">
                <Upload className="h-4 w-4 mr-2" />
                Upload Files
              </Button>
            </div>
          )}
        </div>
      </div>
  );
};

export default FilesPage;
