import React, { useState, useCallback } from 'react';
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Progress,
  Card,
  CardBody,
  Chip,
  Divider,
} from '@heroui/react';
import {
  Upload,
  X,
  File,
  FileText,
  Image,
  Archive,
  CheckCircle,
  AlertCircle,
  Loader2,
} from 'lucide-react';

interface FileUpload {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

interface FileUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadComplete: (files: File[]) => void;
}

export const FileUploadModal: React.FC<FileUploadModalProps> = ({
  isOpen,
  onClose,
  onUploadComplete,
}) => {
  const [uploads, setUploads] = useState<FileUpload[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  const getFileIcon = (file: File) => {
    const type = file.type;
    if (type.startsWith('image/')) {
      return <Image className="h-5 w-5 text-success" />;
    } else if (type.includes('text') || type.includes('document') || type.includes('pdf')) {
      return <FileText className="h-5 w-5 text-primary" />;
    } else if (type.includes('zip') || type.includes('rar') || type.includes('archive')) {
      return <Archive className="h-5 w-5 text-secondary" />;
    }
    return <File className="h-5 w-5 text-default-500" />;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFiles = useCallback((files: FileList) => {
    const newUploads: FileUpload[] = Array.from(files).map(file => ({
      id: Math.random().toString(36).substring(2, 11),
      file,
      progress: 0,
      status: 'pending',
    }));

    setUploads(prev => [...prev, ...newUploads]);

    // Simulate upload process
    newUploads.forEach(upload => {
      simulateUpload(upload.id);
    });
  }, []);

  const simulateUpload = (uploadId: string) => {
    setUploads(prev => prev.map(upload => 
      upload.id === uploadId 
        ? { ...upload, status: 'uploading' }
        : upload
    ));

    const interval = setInterval(() => {
      setUploads(prev => prev.map(upload => {
        if (upload.id === uploadId) {
          const newProgress = Math.min(upload.progress + Math.random() * 30, 100);
          
          if (newProgress >= 100) {
            clearInterval(interval);
            // Simulate random success/error
            const isSuccess = Math.random() > 0.1; // 90% success rate
            return {
              ...upload,
              progress: 100,
              status: isSuccess ? 'success' : 'error',
              error: isSuccess ? undefined : 'Upload failed. Please try again.',
            };
          }
          
          return { ...upload, progress: newProgress };
        }
        return upload;
      }));
    }, 200);
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFiles(files);
    }
  }, [handleFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
  }, [handleFiles]);

  const removeUpload = (uploadId: string) => {
    setUploads(prev => prev.filter(upload => upload.id !== uploadId));
  };

  const handleComplete = () => {
    const successfulFiles = uploads
      .filter(upload => upload.status === 'success')
      .map(upload => upload.file);
    
    onUploadComplete(successfulFiles);
    setUploads([]);
    onClose();
  };

  const allCompleted = uploads.length > 0 && uploads.every(upload => 
    upload.status === 'success' || upload.status === 'error'
  );

  const hasSuccessful = uploads.some(upload => upload.status === 'success');

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose}
      size="2xl"
      scrollBehavior="inside"
      classNames={{
        backdrop: "bg-gradient-to-t from-zinc-900 to-zinc-900/10 backdrop-opacity-20"
      }}
    >
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-xl font-semibold">Upload Files</h2>
          <p className="text-sm text-default-500">
            Drag and drop files or click to browse
          </p>
        </ModalHeader>
        
        <ModalBody>
          {/* Upload Area */}
          <Card
            className={`border-2 border-dashed transition-all duration-200 ${
              isDragOver
                ? 'border-primary bg-primary-50'
                : 'border-default-300 hover:border-default-400'
            }`}
          >
            <CardBody
              className="p-8 text-center cursor-pointer"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <Upload className={`h-12 w-12 mx-auto mb-4 ${
                isDragOver ? 'text-primary' : 'text-default-400'
              }`} />
              <h3 className="text-lg font-medium mb-2">
                {isDragOver ? 'Drop files here' : 'Choose files to upload'}
              </h3>
              <p className="text-default-500 mb-4">
                Support for CSV, Excel, PDF, images and more
              </p>
              <Button color="primary" variant="flat">
                Browse Files
              </Button>
              <input
                id="file-input"
                type="file"
                multiple
                className="hidden"
                onChange={handleFileSelect}
                accept=".csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg,.gif,.zip,.rar"
              />
            </CardBody>
          </Card>

          {/* Upload Progress */}
          {uploads.length > 0 && (
            <div className="space-y-3 mt-4">
              <Divider />
              <h4 className="font-medium text-default-700">Upload Progress</h4>
              
              {uploads.map((upload) => (
                <Card key={upload.id} className="shadow-sm">
                  <CardBody className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0">
                        {getFileIcon(upload.file)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm font-medium truncate">
                            {upload.file.name}
                          </p>
                          <div className="flex items-center gap-2">
                            {upload.status === 'uploading' && (
                              <Loader2 className="h-4 w-4 animate-spin text-primary" />
                            )}
                            {upload.status === 'success' && (
                              <CheckCircle className="h-4 w-4 text-success" />
                            )}
                            {upload.status === 'error' && (
                              <AlertCircle className="h-4 w-4 text-danger" />
                            )}
                            <Button
                              isIconOnly
                              size="sm"
                              variant="light"
                              onPress={() => removeUpload(upload.id)}
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 mb-2">
                          <Chip size="sm" variant="flat" color="default">
                            {formatFileSize(upload.file.size)}
                          </Chip>
                          <Chip 
                            size="sm" 
                            variant="flat"
                            color={
                              upload.status === 'success' ? 'success' :
                              upload.status === 'error' ? 'danger' :
                              upload.status === 'uploading' ? 'primary' : 'default'
                            }
                          >
                            {upload.status}
                          </Chip>
                        </div>
                        
                        {upload.status !== 'pending' && (
                          <Progress
                            value={upload.progress}
                            color={
                              upload.status === 'success' ? 'success' :
                              upload.status === 'error' ? 'danger' : 'primary'
                            }
                            size="sm"
                            className="mb-1"
                          />
                        )}
                        
                        {upload.error && (
                          <p className="text-xs text-danger mt-1">{upload.error}</p>
                        )}
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          )}
        </ModalBody>
        
        <ModalFooter>
          <Button variant="light" onPress={onClose}>
            Cancel
          </Button>
          {allCompleted && hasSuccessful && (
            <Button color="primary" onPress={handleComplete}>
              Complete Upload
            </Button>
          )}
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
