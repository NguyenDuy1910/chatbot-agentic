# Admin Management Dashboard

This project now includes a comprehensive admin management system with the following features:

## 🚀 Features Added

### 1. **File Upload in Chat**
- **Paperclip icon** in chat input for attaching files
- **File preview** with name, size, and type before sending
- **Image preview** with thumbnail display
- **File download** functionality in message bubbles
- **Multiple file types** supported: images, PDFs, documents, text files
- **File size limits** and type validation
- **Visual file indicators** (different icons for different file types)

### 2. **Admin Dashboard** (`/admin`)
- **Secure login** with demo credentials (admin/admin123)
- **Overview statistics** with visual cards and charts
- **Real-time data** with refresh functionality
- **Export reports** in JSON format

### 3. **User Management**
- **User list** with search and filtering
- **User status management** (Active, Inactive, Banned)
- **Activity tracking** (total chats, messages, last active)
- **User role badges** (Admin/User with crown icons)
- **Bulk actions** for managing multiple users
- **User chat history** access

### 4. **Chat Analytics & Visualization**
- **Interactive charts** for messages per day
- **User growth tracking** over time
- **Popular prompts** analysis with usage statistics
- **Real-time activity** monitoring
- **System performance** metrics

### 5. **Enhanced Prompt Management**
- **Full CRUD operations** for prompts
- **Category organization** (General, Coding, Creative, etc.)
- **Usage statistics** tracking
- **Bulk import/export** functionality
- **Active/Inactive status** management
- **Search and filtering** capabilities
- **Popular prompts** ranking

### 6. **System Settings**
- **File upload configuration** (size limits, allowed types)
- **Chat settings** (history limits, rate limiting)
- **Security controls** (maintenance mode)
- **System health monitoring**
- **Advanced danger zone** actions

## 🎨 UI/UX Improvements

### Enhanced Components
- **Modern card layouts** with gradients and shadows
- **Interactive charts** with hover effects
- **Status badges** with color coding
- **Progress bars** for analytics
- **Responsive design** for all screen sizes
- **Loading states** and error handling
- **Smooth animations** and transitions

### File Upload UX
- **Drag-and-drop feel** with hover states
- **File type icons** (document, image, generic)
- **Size formatting** (KB, MB, GB)
- **Remove attachments** with confirmation
- **Visual feedback** during upload

## 🔧 Technical Architecture

### New Components Structure
```
src/
  components/
    admin/
      AdminDashboard.tsx       # Main admin layout
      StatisticsOverview.tsx   # KPI cards and metrics
      UserManagement.tsx       # User CRUD operations
      ChatVisualization.tsx    # Analytics charts
      SystemSettings.tsx       # Configuration panel
      AdminPromptManagement.tsx # Enhanced prompt management
    ui/
      Card.tsx                 # Reusable card component
      Table.tsx                # Data table with sorting
      Tabs.tsx                 # Navigation tabs
  types/
    admin.ts                   # Admin-specific types
  lib/
    adminAPI.ts                # Admin API functions
  AdminApp.tsx                 # Admin app wrapper
```

### File Upload Integration
- **FileAttachment interface** in chat types
- **Enhanced ChatInput** with file handling
- **Updated MessageBubble** for file display
- **Blob URL management** for file previews
- **Memory cleanup** when removing files

## 🚀 Getting Started

### Access the Admin Panel
1. Start the development server: `npm run dev`
2. Navigate to `/admin` in your browser
3. Login with demo credentials:
   - Username: `admin`
   - Password: `admin123`

### Using File Upload
1. In the chat interface, click the paperclip icon
2. Select one or multiple files
3. Preview files before sending
4. Send message with or without text
5. Files appear in chat with download options

### Admin Features Tour
1. **Overview**: Dashboard with key metrics and recent activity
2. **Users**: Manage user accounts, view activity, change status
3. **Analytics**: Interactive charts and usage statistics
4. **Prompts**: Create, edit, and manage prompt templates
5. **Settings**: Configure system parameters and security

## 🔒 Security Features

- **Role-based access** (Admin/User separation)
- **Secure authentication** flow
- **File type validation** and size limits
- **Maintenance mode** capability
- **Activity monitoring** and audit trails
- **Session management** controls

## 📱 Mobile Responsive

- **Responsive grid layouts** that adapt to screen size
- **Mobile-optimized** admin interface
- **Touch-friendly** interactions
- **Collapsible navigation** for smaller screens
- **Optimized file upload** for mobile devices

## 🎯 Demo Data

The admin dashboard includes realistic mock data:
- **125 total users** with varied activity levels
- **Sample chat statistics** and growth metrics
- **Popular prompts** with usage rankings
- **System health** indicators
- **File upload** examples and previews

## 🔄 Real-time Features

- **Auto-refresh** dashboard data
- **Live user activity** indicators
- **Real-time charts** updates
- **System status** monitoring
- **Instant file preview** during upload

This admin system provides a complete management solution for monitoring users, analyzing chat data, managing prompts, and configuring system settings, all while maintaining the existing chat functionality with enhanced file upload capabilities.
