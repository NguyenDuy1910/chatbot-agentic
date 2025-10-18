import React, { useState } from 'react';
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Card,
  CardBody,
  Input,
} from '@heroui/react';
import {
  Database,
  Globe,
  Webhook,
  Key,
  Folder,
  MessageSquare,
  BarChart,
  CreditCard,
  Mail,
  Smartphone,
  Share2,
  Users,
  Building,
  Settings,
  Plug,
  Search,
} from 'lucide-react';

interface ConnectionType {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface ConnectionTypeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectType: (typeId: string) => void;
}

const connectionTypes: ConnectionType[] = [
  {
    id: 'postgresql',
    name: 'PostgreSQL',
    description: 'Connect to PostgreSQL databases with full schema introspection',
    icon: <Database className="h-6 w-6" />,
    color: 'from-blue-500 to-purple-500',
  },
  {
    id: 'athena',
    name: 'Amazon Athena',
    description: 'Query data in S3 using Athena with serverless compute',
    icon: <Globe className="h-6 w-6" />,
    color: 'from-orange-500 to-yellow-500',
  },
  {
    id: 'duckdb',
    name: 'DuckDB',
    description: 'Connect to DuckDB for fast analytical queries',
    icon: <BarChart className="h-6 w-6" />,
    color: 'from-green-500 to-emerald-500',
  },
  // Uncomment and add more when implemented
  // {
  //   id: 'mysql',
  //   name: 'MySQL',
  //   description: 'Connect to MySQL databases',
  //   icon: <Database className="h-6 w-6" />,
  //   color: 'from-blue-400 to-cyan-500',
  // },
  // {
  //   id: 'api',
  //   name: 'REST API',
  //   description: 'Connect to REST APIs',
  //   icon: <Webhook className="h-6 w-6" />,
  //   color: 'from-green-500 to-emerald-500',
  // },
];

export const ConnectionTypeModal: React.FC<ConnectionTypeModalProps> = ({
  isOpen,
  onClose,
  onSelectType,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredTypes = connectionTypes.filter(
    (type) =>
      type.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      type.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectType = (typeId: string) => {
    onSelectType(typeId);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="5xl"
      scrollBehavior="inside"
      classNames={{
        base: "bg-white",
        backdrop: "bg-black/50 backdrop-blur-sm",
      }}
    >
      <ModalContent>
        {(onClose) => (
          <>
            <ModalHeader className="flex flex-col gap-1 border-b pb-4">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Choose Connection Type
              </h2>
              <p className="text-sm text-default-600 font-normal">
                Select the type of connection you want to create
              </p>
            </ModalHeader>
            <ModalBody className="py-6">
              {/* Search Bar */}
              <div className="mb-6">
                <Input
                  placeholder="Search connection types..."
                  value={searchTerm}
                  onValueChange={setSearchTerm}
                  startContent={<Search className="h-4 w-4 text-default-400" />}
                  classNames={{
                    input: "text-sm",
                    inputWrapper: "shadow-sm",
                  }}
                />
              </div>

              {/* Connection Types Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {filteredTypes.map((type) => (
                  <Card
                    key={type.id}
                    isPressable
                    onPress={() => handleSelectType(type.id)}
                    className="group hover:shadow-2xl transition-all duration-300 border-2 border-transparent hover:border-primary-200 cursor-pointer hover:scale-[1.03]"
                  >
                    <CardBody className="p-6 flex flex-col items-center text-center min-h-[240px] gap-4">
                      <div
                        className={`p-6 rounded-2xl bg-gradient-to-br ${type.color} text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}
                      >
                        {type.icon}
                      </div>
                      <div className="flex-1 flex flex-col justify-center space-y-2">
                        <h3 className="font-bold text-xl text-foreground">
                          {type.name}
                        </h3>
                        <p className="text-sm text-default-600 leading-relaxed">
                          {type.description}
                        </p>
                      </div>
                      <Button
                        color="primary"
                        size="lg"
                        className={`w-full bg-gradient-to-r ${type.color} text-white font-semibold shadow-lg hover:shadow-xl transition-all`}
                      >
                        Select {type.name}
                      </Button>
                    </CardBody>
                  </Card>
                ))}
              </div>

              {filteredTypes.length === 0 && (
                <div className="text-center py-12">
                  <Plug className="h-12 w-12 text-default-300 mx-auto mb-3" />
                  <p className="text-default-500">No connection types found</p>
                  <p className="text-sm text-default-400 mt-1">
                    Try adjusting your search
                  </p>
                </div>
              )}
            </ModalBody>
            <ModalFooter className="border-t pt-4">
              <Button
                color="default"
                variant="flat"
                onPress={onClose}
              >
                Cancel
              </Button>
            </ModalFooter>
          </>
        )}
      </ModalContent>
    </Modal>
  );
};
