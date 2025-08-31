import React, { useState } from 'react';
import { User } from '@/types/features/admin';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/shared/ui/Card';
import { 
  Table, 
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell 
} from '@/components/shared/ui/Table';
import { Button } from '@/components/shared/ui/Button';
import { Badge } from '@/components/shared/ui/Badge';
import { 
  MoreHorizontal, 
  Eye, 
  Ban, 
  CheckCircle, 
  Trash2,
  Crown,
  Clock
} from 'lucide-react';

interface UserManagementProps {
  users: User[];
  onUpdateUserStatus: (userId: string, status: User['status']) => void;
  onDeleteUser: (userId: string) => void;
  onViewUserChats: (userId: string) => void;
}

export const UserManagement: React.FC<UserManagementProps> = ({
  users,
  onUpdateUserStatus,
  onDeleteUser,
  onViewUserChats
}) => {
  const [showActions, setShowActions] = useState<string | null>(null);

  const getStatusBadge = (status: User['status']) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Active</Badge>;
      case 'inactive':
        return <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">Inactive</Badge>;
      case 'banned':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Banned</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  const getRoleBadge = (role: User['role']) => {
    return role === 'admin' ? (
      <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-100 flex items-center gap-1">
        <Crown className="h-3 w-3" />
        Admin
      </Badge>
    ) : (
      <Badge variant="outline">User</Badge>
    );
  };

  const formatLastActive = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const handleStatusChange = (userId: string, newStatus: User['status']) => {
    onUpdateUserStatus(userId, newStatus);
    setShowActions(null);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Crown className="h-5 w-5 text-purple-500" />
            User Management
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button size="sm">
              Export Users
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Activity</TableHead>
              <TableHead>Last Active</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium text-foreground">{user.name}</div>
                      <div className="text-sm text-muted-foreground">{user.email}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  {getRoleBadge(user.role)}
                </TableCell>
                <TableCell>
                  {getStatusBadge(user.status)}
                </TableCell>
                <TableCell>
                  <div className="space-y-1">
                    <div className="text-sm font-medium">{user.totalChats} chats</div>
                    <div className="text-xs text-muted-foreground">{user.totalMessages} messages</div>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {formatLastActive(user.lastActive)}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="relative">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowActions(showActions === user.id ? null : user.id)}
                      className="h-8 w-8 p-0"
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                    
                    {showActions === user.id && (
                      <div className="absolute right-0 top-8 w-48 bg-background border rounded-lg shadow-lg z-50 py-1">
                        <button
                          onClick={() => onViewUserChats(user.id)}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-muted flex items-center gap-2"
                        >
                          <Eye className="h-4 w-4" />
                          View Chats
                        </button>
                        
                        {user.status !== 'active' && (
                          <button
                            onClick={() => handleStatusChange(user.id, 'active')}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-muted flex items-center gap-2 text-green-600"
                          >
                            <CheckCircle className="h-4 w-4" />
                            Activate
                          </button>
                        )}
                        
                        {user.status !== 'banned' && user.role !== 'admin' && (
                          <button
                            onClick={() => handleStatusChange(user.id, 'banned')}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-muted flex items-center gap-2 text-red-600"
                          >
                            <Ban className="h-4 w-4" />
                            Ban User
                          </button>
                        )}
                        
                        {user.role !== 'admin' && (
                          <button
                            onClick={() => onDeleteUser(user.id)}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-muted flex items-center gap-2 text-red-600"
                          >
                            <Trash2 className="h-4 w-4" />
                            Delete User
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};
