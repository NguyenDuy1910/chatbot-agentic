# Management URI System

## Overview

The chatbot application now includes a comprehensive URI management system for admin pages. This system provides structured navigation, URL management, and proper routing for all administrative functions.

## Available Management URLs

### Base Routes
- `/` - Main chatbot interface (user-facing)
- `/admin` - Admin login/dashboard

### Admin Management Pages
- `/admin` - Dashboard Overview (default)
- `/admin/users` - User Management
- `/admin/chats` - Chat Analytics  
- `/admin/prompts` - Prompt Management
- `/admin/settings` - System Settings
- `/admin/uris` - URI Management Directory

## Features

### 1. URL Router (`/src/lib/router.ts`)
- **AdminRouter class** - Centralized routing logic
- **Route configuration** - Structured route definitions
- **URL parameter handling** - Query string management
- **Navigation utilities** - Programmatic navigation
- **Breadcrumb generation** - Dynamic breadcrumbs

### 2. React Router Hook (`useAdminRouter`)
```typescript
const { currentRoute, navigateTo, getQueryParams, buildUrl } = useAdminRouter();
```

### 3. Management URI Page (`/admin/uris`)
- **Complete route directory** - All available admin URLs
- **Current page information** - Active route details
- **Navigation buttons** - Direct page navigation
- **URL copying** - Copy URLs to clipboard
- **Route documentation** - URL pattern guidelines

### 4. Enhanced Navigation
- **Tab-based navigation** - Visual tab interface
- **URL synchronization** - Browser address bar updates
- **History management** - Browser back/forward support
- **Deep linking** - Direct access to any admin page

## Technical Implementation

### Router Configuration
```typescript
export const adminRoutes: Record<string, AdminRoute> = {
  overview: {
    path: '/admin',
    title: 'Dashboard Overview',
    description: 'Main dashboard with statistics and recent activity',
    component: 'DashboardOverview'
  },
  // ... other routes
};
```

### Navigation Method
```typescript
// Navigate to a specific admin page
AdminRouter.navigateTo('users', { filter: 'active' });

// Build URL with parameters
const url = AdminRouter.buildUrl('chats', { date: '2024-01-01' });

// Get current route information
const currentRoute = AdminRouter.getCurrentRoute();
```

### Component Integration
```typescript
// In React components
import { useAdminRouter } from '@/lib/router';

const { currentRoute, navigateTo } = useAdminRouter();

// Navigate programmatically
const handleNavigate = () => {
  navigateTo('settings');
};
```

## URL Patterns

### Query Parameters
- `?tab=users` - Direct tab navigation
- `?filter=active` - Content filtering
- `?page=2` - Pagination
- `?search=query` - Search terms

### Examples
```
/admin                    -> Dashboard overview
/admin/users?filter=active -> User management with active filter
/admin/chats?date=2024-01-01 -> Chat analytics for specific date
/admin/prompts?category=coding -> Prompts filtered by category
```

## Usage Guide

### Accessing the URI Management Page
1. Log into admin panel (`/admin`)
2. Navigate to "URI Management" tab
3. View all available routes and their URLs
4. Use navigation buttons to visit pages
5. Copy URLs for sharing or bookmarking

### Programmatic Navigation
```typescript
// Direct navigation
AdminRouter.navigateTo('users');

// Navigation with parameters
AdminRouter.navigateTo('chats', { 
  filter: 'recent',
  limit: '50'
});

// Build URLs for links
const userManagementUrl = AdminRouter.buildUrl('users', { 
  status: 'active' 
});
```

### URL Parameter Access
```typescript
// Get current query parameters
const params = AdminRouter.getQueryParams();
const filter = params.filter; // 'active'
const page = params.page;     // '2'
```

## Benefits

1. **SEO Friendly** - Proper URLs for each admin page
2. **Bookmarkable** - Direct links to specific admin functions
3. **Shareable** - URLs can be shared between admin users
4. **Navigation History** - Browser back/forward works properly
5. **Deep Linking** - Direct access to any admin page
6. **Parameter Support** - URL parameters for filtering/pagination
7. **Centralized Management** - All routes defined in one place
8. **Type Safety** - TypeScript interfaces for route configuration

## Browser Compatibility

- Uses HTML5 History API for routing
- Falls back gracefully in older browsers
- No page reloads during navigation
- Maintains application state during navigation

## Future Enhancements

- Route guards for permission-based access
- Dynamic route loading
- Route-based code splitting
- Advanced parameter validation
- Route middleware support

This URI management system provides a solid foundation for scalable admin panel navigation and can be extended as the application grows.
