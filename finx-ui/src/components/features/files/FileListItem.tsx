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

interface FileListItemProps {
  file: FileItem;
  onDelete: (id: string) => void;
  onRename: (id: string, newName: string) => void;
  onDownload: (id: string) => void;
  onView: (id: string) => void;
}

export const FileListItem: React.FC<FileListItemProps> = ({
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
    const iconClass = "h-6 w-6";
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
        className="hover:shadow-md transition-all duration-200 group cursor-pointer h-20"
        isPressable
        onPress={() => onView(file.id)}
      >
        <CardBody className="p-4 h-full">
          <div className="flex items-center gap-4 h-full">
            {/* File Icon */}
            <div className="flex-shrink-0 w-12 h-12 p-3 rounded-lg bg-default-100 group-hover:bg-default-200 transition-colors flex items-center justify-center">
              {getFileIcon(file.type)}
            </div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between h-full">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-foreground truncate mb-1 text-sm" title={file.name}>
                    {file.name}
                  </h3>
                  <div className="flex items-center gap-3 text-xs text-default-500">
                    <span className="flex items-center gap-1">
                      <HardDrive className="h-3 w-3" />
                      {formatFileSize(file.size)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {file.uploadDate.toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Status and Type */}
                <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                  <Chip
                    size="sm"
                    variant="flat"
                    color={getTypeColor(file.type)}
                    className="h-6"
                  >
                    {file.type.charAt(0).toUpperCase() + file.type.slice(1)}
                  </Chip>
                  <Chip
                    size="sm"
                    variant="flat"
                    color={getStatusColor(file.status)}
                    className="h-6"
                  >
                    {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                  </Chip>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 ml-4 flex-shrink-0">
                  <Button
                    size="sm"
                    variant="flat"
                    color="primary"
                    startContent={<Eye className="h-3 w-3" />}
                    onPress={() => onView(file.id)}
                    className="h-8 px-3"
                  >
                    View
                  </Button>
                  <Button
                    isIconOnly
                    size="sm"
                    variant="light"
                    onPress={() => onDownload(file.id)}
                    className="h-8 w-8"
                  >
                    <Download className="h-3 w-3" />
                  </Button>

                  <Dropdown>
                    <DropdownTrigger>
                      <Button
                        isIconOnly
                        size="sm"
                        variant="light"
                        className="h-8 w-8"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownTrigger>
                    <DropdownMenu>
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
              </div>
            </div>
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
