# 🏗️ Frontend Structure Guide - Vikki ChatBot

## 📋 Tổng quan

Project frontend đã được tổ chức lại hoàn toàn theo kiến trúc **feature-based** và **modular**, giúp code dễ bảo trì, mở rộng và phát triển.

## 🎯 Những cải tiến chính

### ✅ Trước khi tổ chức lại
- Components trộn lẫn ở root level
- Routing đơn giản trong main.tsx
- Types phân tán
- Styles không có cấu trúc rõ ràng
- Import paths không nhất quán

### ✅ Sau khi tổ chức lại
- **Feature-based architecture**: Components được nhóm theo tính năng
- **Professional routing system**: Router riêng biệt với authentication
- **Organized types**: Types được phân chia theo shared/features
- **Structured styles**: Theme system và component styles
- **Barrel exports**: Import paths clean và nhất quán

## 📁 Cấu trúc chi tiết

```
src/
├── 📄 main.tsx                 # Entry point với AuthProvider
├── 📄 README.md               # Hướng dẫn cấu trúc
│
├── 📁 assets/                 # Static assets
│   ├── 📁 images/            # Hình ảnh
│   ├── 📁 icons/             # Icons
│   └── 📁 fonts/             # Fonts
│
├── 📁 components/            # React components
│   ├── 📁 shared/           # Components dùng chung
│   │   ├── 📁 ui/          # Basic UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── index.ts    # Barrel export
│   │   ├── AppWithAuth.tsx
│   │   └── index.ts
│   │
│   ├── 📁 features/        # Feature-specific components
│   │   ├── 📁 admin/      # Admin dashboard
│   │   ├── 📁 auth/       # Authentication
│   │   ├── 📁 chat/       # Chat interface
│   │   ├── 📁 connections/ # Database connections
│   │   ├── 📁 database/   # Database management
│   │   ├── 📁 prompts/    # Prompt management
│   │   └── index.ts
│   │
│   └── index.ts           # Main barrel export
│
├── 📁 pages/               # Page components
│   ├── 📁 admin/         # AdminPage.tsx
│   ├── 📁 auth/          # LoginPage.tsx
│   ├── 📁 chat/          # ChatPage.tsx
│   ├── 📁 connections/   # ConnectionsPage.tsx
│   └── index.ts
│
├── 📁 router/             # Routing system
│   ├── AppRouter.tsx     # Main router với auth
│   ├── routes.ts         # Route definitions
│   └── index.ts
│
├── 📁 types/              # TypeScript definitions
│   ├── 📁 shared/        # Common types
│   │   ├── common.ts     # BaseEntity, ApiResponse, etc.
│   │   ├── ui.ts         # UI component types
│   │   └── index.ts
│   ├── 📁 features/      # Feature-specific types
│   │   ├── admin.ts
│   │   ├── auth.ts
│   │   ├── chat.ts
│   │   └── index.ts
│   └── index.ts
│
├── 📁 styles/             # Styling system
│   ├── 📁 themes/        # Theme definitions
│   │   ├── colors.css    # Color palette
│   │   └── typography.css # Typography system
│   ├── 📁 components/    # Component-specific styles
│   ├── 📁 utilities/     # Utility styles & animations
│   └── index.css         # Main styles entry
│
├── 📁 config/             # Configuration
│   ├── env.ts            # Environment variables
│   ├── api.ts            # API configuration
│   └── index.ts
│
├── 📁 constants/          # Application constants
│   ├── app.ts            # App constants
│   ├── ui.ts             # UI constants
│   └── index.ts
│
├── 📁 contexts/           # React contexts
├── 📁 hooks/              # Custom hooks
└── 📁 lib/                # Utility libraries
```

## 🚀 Cách sử dụng

### Import Patterns

```typescript
// ✅ Pages
import { ChatPage, AdminPage } from '@/pages';

// ✅ Shared UI Components
import { Button, Card, Input } from '@/components/shared/ui';

// ✅ Feature Components
import { LoginForm } from '@/components/features/auth';
import { ChatArea } from '@/components/features/chat';
import { AdminDashboard } from '@/components/features/admin';

// ✅ Types
import type { User, ApiResponse } from '@/types/shared';
import type { ChatMessage } from '@/types/features/chat';

// ✅ Config & Constants
import { env, apiConfig } from '@/config';
import { APP_INFO, STORAGE_KEYS } from '@/constants';
```

### Routing System

```typescript
// Router tự động handle authentication
// Các route được protect bằng ProtectedRoute wrapper
// Admin routes yêu cầu role 'admin'

const routes = {
  '/': ChatPage,           // Protected
  '/admin': AdminPage,     // Protected + Admin only
  '/connections': ConnectionsPage, // Protected
  '/login': LoginPage      // Public
};
```

## 🎨 Theme System

### Colors
- CSS Custom Properties trong `styles/themes/colors.css`
- Support dark/light theme
- Consistent color palette

### Typography
- Font system trong `styles/themes/typography.css`
- Responsive font sizes
- Consistent line heights

## 📦 Component Organization

### Shared Components (`components/shared/`)
- **UI Components**: Button, Input, Card, etc.
- **Layout Components**: AppWithAuth, etc.
- **Reusable across features**

### Feature Components (`components/features/`)
- **admin/**: Dashboard, user management, settings
- **auth/**: Login, user profile, user menu
- **chat/**: Chat area, message bubble, typing indicator
- **connections/**: Database connections, connection dashboard
- **database/**: Database management, SQL interface
- **prompts/**: Prompt management, prompt cards

## 🔧 Configuration

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_ADMIN_FEATURES=true
VITE_DEFAULT_THEME=light
```

### API Configuration
- Centralized trong `config/api.ts`
- Endpoint definitions
- Default headers và retry logic

## 📝 Best Practices

1. **Always use barrel exports** - Import từ index files
2. **Feature-based organization** - Group theo tính năng, không theo file type
3. **Consistent naming** - PascalCase cho components, camelCase cho utilities
4. **Type safety** - Sử dụng TypeScript strictly
5. **Absolute imports** - Sử dụng `@/` prefix

## 🔄 Migration Notes

- Tất cả import paths đã được cập nhật
- Components đã được di chuyển vào đúng feature folders
- Types đã được tổ chức lại theo shared/features
- Styles đã được cấu trúc lại với theme system

## 🎯 Next Steps

1. **Testing**: Viết tests cho components mới
2. **Documentation**: Thêm JSDoc cho các components
3. **Performance**: Implement lazy loading cho routes
4. **Accessibility**: Thêm ARIA labels và keyboard navigation
