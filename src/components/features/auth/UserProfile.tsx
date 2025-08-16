import React, { useState } from 'react';
import { Button } from '@/components/shared/ui/Button';
import { Input } from '@/components/shared/ui/Input';
import { Textarea } from '@/components/shared/ui/Textarea';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/shared/ui/Card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/shared/ui/Tabs';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Camera, 
  Save, 
  Lock, 
  Bell, 
  Shield,
  Eye,
  EyeOff
} from 'lucide-react';
import { UserProfile, PasswordUpdate, ProfileUpdate } from '@/types/features/auth';

interface UserProfileProps {
  user: UserProfile;
  onUpdateProfile: (updates: ProfileUpdate) => Promise<void>;
  onUpdatePassword: (passwordData: PasswordUpdate) => Promise<void>;
  loading?: boolean;
}

export const UserProfileComponent: React.FC<UserProfileProps> = ({
  user,
  onUpdateProfile,
  onUpdatePassword,
  loading = false
}) => {
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [selectedAvatar, setSelectedAvatar] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  // Profile form data
  const [profileData, setProfileData] = useState({
    name: user.name,
    bio: user.bio || '',
    phone: user.phone || '',
    location: user.location || '',
    timezone: user.timezone || 'UTC'
  });

  // Password form data
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // Preferences data
  const [preferences, setPreferences] = useState(user.preferences);

  // Handle avatar selection
  const handleAvatarSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedAvatar(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatarPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle profile update
  const handleProfileUpdate = async () => {
    try {
      const updates: ProfileUpdate = {
        ...profileData,
        ...(selectedAvatar && { avatar: selectedAvatar })
      };
      
      await onUpdateProfile(updates);
      setIsEditing(false);
      setSelectedAvatar(null);
      setAvatarPreview(null);
    } catch (error) {
      console.error('Profile update failed:', error);
    }
  };

  // Handle password update
  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await onUpdatePassword(passwordData);
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      console.error('Password update failed:', error);
    }
  };

  // Format date
  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Profile Settings</h1>
          <p className="text-muted-foreground">Manage your account settings and preferences</p>
        </div>
        {activeTab === 'profile' && (
          <Button
            onClick={() => isEditing ? handleProfileUpdate() : setIsEditing(true)}
            disabled={loading}
            className="flex items-center gap-2"
          >
            {isEditing ? (
              <>
                <Save className="h-4 w-4" />
                Save Changes
              </>
            ) : (
              <>
                <User className="h-4 w-4" />
                Edit Profile
              </>
            )}
          </Button>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Lock className="h-4 w-4" />
            Security
          </TabsTrigger>
          <TabsTrigger value="preferences" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Preferences
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Personal Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Avatar Section */}
              <div className="flex items-center gap-6">
                <div className="relative">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center text-primary-foreground text-2xl font-bold overflow-hidden">
                    {avatarPreview || user.avatar ? (
                      <img
                        src={avatarPreview || user.avatar}
                        alt="Profile"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      user.name.charAt(0).toUpperCase()
                    )}
                  </div>
                  {isEditing && (
                    <label className="absolute bottom-0 right-0 bg-primary text-primary-foreground rounded-full p-1 cursor-pointer hover:bg-primary/90 transition-colors">
                      <Camera className="h-4 w-4" />
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleAvatarSelect}
                        className="hidden"
                      />
                    </label>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">{user.name}</h3>
                  <p className="text-muted-foreground">{user.email}</p>
                  <p className="text-sm text-muted-foreground">
                    Member since {formatDate(user.createdAt)}
                  </p>
                </div>
              </div>

              {/* Profile Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Full Name
                  </label>
                  <Input
                    value={profileData.name}
                    onChange={(e) => setProfileData(prev => ({ ...prev, name: e.target.value }))}
                    disabled={!isEditing || loading}
                    placeholder="Enter your full name"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    Email Address
                  </label>
                  <Input
                    value={user.email}
                    disabled
                    className="bg-muted"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <Phone className="h-4 w-4" />
                    Phone Number
                  </label>
                  <Input
                    value={profileData.phone}
                    onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
                    disabled={!isEditing || loading}
                    placeholder="Enter your phone number"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    Location
                  </label>
                  <Input
                    value={profileData.location}
                    onChange={(e) => setProfileData(prev => ({ ...prev, location: e.target.value }))}
                    disabled={!isEditing || loading}
                    placeholder="Enter your location"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Bio</label>
                <Textarea
                  value={profileData.bio}
                  onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
                  disabled={!isEditing || loading}
                  placeholder="Tell us a bit about yourself"
                  rows={3}
                />
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">{user.totalChats}</div>
                  <div className="text-sm text-muted-foreground">Total Chats</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{user.totalMessages}</div>
                  <div className="text-sm text-muted-foreground">Messages Sent</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{user.role}</div>
                  <div className="text-sm text-muted-foreground">Account Type</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{user.status}</div>
                  <div className="text-sm text-muted-foreground">Status</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Change Password
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePasswordUpdate} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Current Password</label>
                  <div className="relative">
                    <Input
                      type={showPasswords.current ? 'text' : 'password'}
                      value={passwordData.currentPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                      placeholder="Enter current password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">New Password</label>
                  <div className="relative">
                    <Input
                      type={showPasswords.new ? 'text' : 'password'}
                      value={passwordData.newPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                      placeholder="Enter new password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Confirm New Password</label>
                  <div className="relative">
                    <Input
                      type={showPasswords.confirm ? 'text' : 'password'}
                      value={passwordData.confirmPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      placeholder="Confirm new password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <Button type="submit" disabled={loading} className="w-full">
                  {loading ? 'Updating...' : 'Update Password'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preferences Tab */}
        <TabsContent value="preferences" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Email Notifications</div>
                  <div className="text-sm text-muted-foreground">Receive notifications via email</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.notifications.email}
                  onChange={(e) => setPreferences(prev => ({
                    ...prev,
                    notifications: { ...prev.notifications, email: e.target.checked }
                  }))}
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Push Notifications</div>
                  <div className="text-sm text-muted-foreground">Receive push notifications</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.notifications.push}
                  onChange={(e) => setPreferences(prev => ({
                    ...prev,
                    notifications: { ...prev.notifications, push: e.target.checked }
                  }))}
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Chat Notifications</div>
                  <div className="text-sm text-muted-foreground">Receive notifications for new messages</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.notifications.chat}
                  onChange={(e) => setPreferences(prev => ({
                    ...prev,
                    notifications: { ...prev.notifications, chat: e.target.checked }
                  }))}
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Privacy
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Show Profile</div>
                  <div className="text-sm text-muted-foreground">Make your profile visible to others</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.privacy.showProfile}
                  onChange={(e) => setPreferences(prev => ({
                    ...prev,
                    privacy: { ...prev.privacy, showProfile: e.target.checked }
                  }))}
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Show Activity</div>
                  <div className="text-sm text-muted-foreground">Show your last active status</div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.privacy.showActivity}
                  onChange={(e) => setPreferences(prev => ({
                    ...prev,
                    privacy: { ...prev.privacy, showActivity: e.target.checked }
                  }))}
                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
