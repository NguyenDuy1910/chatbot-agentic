# Frontend Project Structure

## 📁 Cấu trúc thư mục

```
src/
├── assets/                 # Static assets
│   ├── images/            # Image files
│   ├── icons/             # Icon files
│   └── fonts/             # Font files
│
├── components/            # React components
│   ├── shared/           # Shared/reusable components
│   │   ├── ui/          # Basic UI components (Button, Input, etc.)
│   │   └── AppWithAuth.tsx
│   └── features/        # Feature-specific components
│       ├── admin/       # Admin feature components
│       ├── auth/        # Authentication components
│       ├── chat/        # Chat feature components
│       ├── connections/ # Database connections
│       ├── database/    # Database management
│       └── prompts/     # Prompt management
│
├── config/               # Configuration files
│   ├── env.ts           # Environment variables
│   └── api.ts           # API configuration
│
├── constants/            # Application constants
│   ├── app.ts           # App-wide constants
│   └── ui.ts            # UI constants
│
├── contexts/             # React contexts
│   └── AuthContext.tsx  # Authentication context
│
├── hooks/                # Custom React hooks
│   └── useChat.ts       # Chat functionality hook
│
├── lib/                  # Utility libraries
│   ├── api.ts           # API client
│   ├── utils.ts         # Utility functions
│   └── router.ts        # Router utilities
│
├── pages/                # Page components
│   ├── admin/           # Admin pages
│   ├── auth/            # Authentication pages
│   ├── chat/            # Chat pages
│   └── connections/     # Connection pages
│
├── router/               # Routing configuration
│   ├── AppRouter.tsx    # Main router component
│   └── routes.ts        # Route definitions
│
├── styles/               # Styling files
│   ├── themes/          # Theme definitions
│   │   ├── colors.css   # Color palette
│   │   └── typography.css # Typography system
│   ├── components/      # Component-specific styles
│   ├── utilities/       # Utility styles
│   └── index.css        # Main styles entry
│
├── types/                # TypeScript type definitions
│   ├── shared/          # Shared types
│   │   ├── common.ts    # Common types
│   │   └── ui.ts        # UI component types
│   └── features/        # Feature-specific types
│       ├── admin.ts
│       ├── auth.ts
│       ├── chat.ts
│       ├── connections.ts
│       ├── database.ts
│       └── prompt.ts
│
└── main.tsx              # Application entry point
```

## 🎯 Nguyên tắc tổ chức

### 1. **Feature-based Organization**
- Components được tổ chức theo features (admin, auth, chat, etc.)
- Mỗi feature có thể có components, types, và styles riêng

### 2. **Shared vs Feature-specific**
- `shared/`: Components, types, utilities dùng chung
- `features/`: Components, types chỉ dùng cho feature cụ thể

### 3. **Barrel Exports**
- Mỗi thư mục có `index.ts` để export các modules
- Import dễ dàng: `import { Button } from '@/components/shared/ui'`

### 4. **Type Safety**
- Types được tổ chức theo modules
- Shared types cho các interface chung
- Feature types cho business logic cụ thể

## 📦 Import Patterns

### Recommended imports:
```typescript
// Pages
import { ChatPage, AdminPage } from '@/pages';

// Shared components
import { Button, Card, Input } from '@/components/shared/ui';
import { AppWithAuth } from '@/components/shared';

// Feature components
import { ChatArea, MessageBubble } from '@/components/features/chat';
import { LoginForm } from '@/components/features/auth';

// Types
import type { User, ApiResponse } from '@/types/shared';
import type { ChatMessage } from '@/types/features';

// Config & Constants
import { env, apiConfig } from '@/config';
import { APP_INFO, STORAGE_KEYS } from '@/constants';
```

## 🎨 Styling Strategy

### 1. **CSS Custom Properties**
- Theme variables in `styles/themes/`
- Consistent color palette and typography

### 2. **Tailwind CSS**
- Utility-first approach
- Custom utilities in `styles/utilities/`

### 3. **Component Styles**
- Component-specific styles in `styles/components/`
- Scoped to avoid conflicts

## 🔧 Configuration

### Environment Variables
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# Authentication
VITE_JWT_SECRET=your-secret-key
VITE_AUTH_COOKIE_NAME=vikki_auth_token

# Feature Flags
VITE_ENABLE_ADMIN_FEATURES=true
VITE_ENABLE_DEBUG_MODE=false

# UI Configuration
VITE_DEFAULT_THEME=light
VITE_ENABLE_DARK_MODE=true
```

## 🚀 Best Practices

1. **Always use barrel exports** for cleaner imports
2. **Keep components small and focused** on single responsibility
3. **Use TypeScript strictly** - no `any` types
4. **Follow naming conventions**:
   - Components: PascalCase
   - Files: PascalCase for components, camelCase for utilities
   - Folders: lowercase with hyphens
5. **Organize by feature** rather than by file type
6. **Use absolute imports** with `@/` prefix
