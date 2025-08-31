import React, { useState } from 'react';
import {
  Card,
  CardBody,
  Button,
  Chip,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Input,
  useDisclosure,
} from '@heroui/react';
import {
  FileText,
  Image,
  Archive,
  File,
  Download,
  Trash2,
  Edit3,
  Eye,
  MoreVertical,
  Calendar,
  HardDrive,
} from 'lucide-react';

interface FileItem {
  id: string;
  name: string;
  type: 'document' | 'image' | 'archive' | 'other';
  size: number;
  uploadDate: Date;
  lastAccessed: Date;
  status: 'processing' | 'ready' | 'error';
}

interface FileCardProps {
  file: FileItem;
  onDelete: (id: string) => void;
  onRename: (id: string, newName: string) => void;
  onDownload: (id: string) => void;
  onView: (id: string) => void;
}

export const FileCard: React.FC<FileCardProps> = ({
  file,
  onDelete,
  onRename,
  onDownload,
  onView,
}) => {
  const [newName, setNewName] = useState(file.name);
  const { isOpen: isRenameOpen, onOpen: onRenameOpen, onClose: onRenameClose } = useDisclosure();
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure();

  const getFileIcon = (type: string) => {
    const iconClass = "h-8 w-8";
    switch (type) {
      case 'document':
        return <FileText className={`${iconClass} text-primary`} />;
      case 'image':
        return <Image className={`${iconClass} text-success`} />;
      case 'archive':
        return <Archive className={`${iconClass} text-secondary`} />;
      default:
        return <File className={`${iconClass} text-default-500`} />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'success';
      case 'processing':
        return 'warning';
      case 'error':
        return 'danger';
      default:
        return 'default';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'document':
        return 'primary';
      case 'image':
        return 'success';
      case 'archive':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const handleRename = () => {
    if (newName.trim() && newName !== file.name) {
      onRename(file.id, newName.trim());
    }
    onRenameClose();
  };

  const handleDelete = () => {
    onDelete(file.id);
    onDeleteClose();
  };

  return (
    <>
      <Card 
        className="hover:shadow-lg transition-all duration-200 group"
        isPressable
        onPress={() => onView(file.id)}
      >
        <CardBody className="p-4">
          {/* Header with icon and actions */}
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-xl bg-default-100 group-hover:bg-default-200 transition-colors">
              {getFileIcon(file.type)}
            </div>
            
            <Dropdown>
              <DropdownTrigger>
                <Button
                  isIconOnly
                  size="sm"
                  variant="light"
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownTrigger>
              <DropdownMenu>
                <DropdownItem
                  key="view"
                  startContent={<Eye className="h-4 w-4" />}
                  onPress={() => onView(file.id)}
                >
                  View
                </DropdownItem>
                <DropdownItem
                  key="download"
                  startContent={<Download className="h-4 w-4" />}
                  onPress={() => onDownload(file.id)}
                >
                  Download
                </DropdownItem>
                <DropdownItem
                  key="rename"
                  startContent={<Edit3 className="h-4 w-4" />}
                  onPress={onRenameOpen}
                >
                  Rename
                </DropdownItem>
                <DropdownItem
                  key="delete"
                  className="text-danger"
                  color="danger"
                  startContent={<Trash2 className="h-4 w-4" />}
                  onPress={onDeleteOpen}
                >
                  Delete
                </DropdownItem>
              </DropdownMenu>
            </Dropdown>
          </div>

          {/* File info */}
          <div className="mb-4">
            <h3 className="font-semibold text-foreground mb-1 truncate" title={file.name}>
              {file.name}
            </h3>
            <p className="text-sm text-default-500 flex items-center gap-1">
              <HardDrive className="h-3 w-3" />
              {formatFileSize(file.size)}
            </p>
          </div>

          {/* Status and type badges */}
          <div className="flex items-center gap-2 mb-4">
            <Chip
              size="sm"
              variant="flat"
              color={getTypeColor(file.type)}
            >
              {file.type.charAt(0).toUpperCase() + file.type.slice(1)}
            </Chip>
            <Chip
              size="sm"
              variant="flat"
              color={getStatusColor(file.status)}
            >
              {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
            </Chip>
          </div>

          {/* Dates */}
          <div className="space-y-1 mb-4">
            <div className="flex items-center gap-1 text-xs text-default-500">
              <Calendar className="h-3 w-3" />
              <span>Uploaded: {file.uploadDate.toLocaleDateString()}</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-default-500">
              <Eye className="h-3 w-3" />
              <span>Last accessed: {file.lastAccessed.toLocaleDateString()}</span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              color="primary"
              variant="flat"
              className="flex-1"
              startContent={<Eye className="h-3 w-3" />}
              onPress={() => onView(file.id)}
            >
              View
            </Button>
            <Button
              isIconOnly
              size="sm"
              variant="light"
              onPress={() => onDownload(file.id)}
            >
              <Download className="h-3 w-3" />
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Rename Modal */}
      <Modal isOpen={isRenameOpen} onClose={onRenameClose}>
        <ModalContent>
          <ModalHeader>
            <h3>Rename File</h3>
          </ModalHeader>
          <ModalBody>
            <Input
              label="File Name"
              value={newName}
              onValueChange={setNewName}
              placeholder="Enter new file name"
              autoFocus
            />
          </ModalBody>
          <ModalFooter>
            <Button variant="light" onPress={onRenameClose}>
              Cancel
            </Button>
            <Button color="primary" onPress={handleRename}>
              Rename
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={isDeleteOpen} onClose={onDeleteClose}>
        <ModalContent>
          <ModalHeader>
            <h3>Delete File</h3>
          </ModalHeader>
          <ModalBody>
            <p>Are you sure you want to delete <strong>{file.name}</strong>?</p>
            <p className="text-sm text-default-500">This action cannot be undone.</p>
          </ModalBody>
          <ModalFooter>
            <Button variant="light" onPress={onDeleteClose}>
              Cancel
            </Button>
            <Button color="danger" onPress={handleDelete}>
              Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};
