# Component Organization Guide

## 📁 Directory Structure

```
src/components/
├── common/              # Reusable components across all features
├── shared/              # Infrastructure components (layout, auth, UI primitives)
├── features/            # Feature-specific components
├── charts/              # ⚠️ DEPRECATED - Use features/analytics/
└── demo/                # Development demos (not for production)
```

## 🎯 Component Categories

### 1. Common Components (`common/`)
**Purpose**: Highly reusable, generic components that can be used across multiple features.

**Examples**:
- Generic cards
- Form fields
- List views
- Modal wrappers

**When to use**: Component has no business logic and can be used in any feature.

### 2. Shared Components (`shared/`)
**Purpose**: Infrastructure and foundational components.

**Subdirectories**:
- `auth/` - Authentication components (ProtectedRoute, etc.)
- `layout/` - Layout components (Header, Sidebar, Footer, etc.)
- `ui/` - Base UI primitives (Button, Input, Select, etc.)

**When to use**: Component provides core functionality or UI primitives.

### 3. Feature Components (`features/`)
**Purpose**: Business-specific components organized by feature domain.

#### Current Features:

##### `features/admin/`
Admin dashboard and system management components.

**Components**:
- AdminDashboard
- UserManagement
- SystemSettings
- DashboardOverview
- StatisticsOverview

##### `features/analytics/`
Charts, metrics, and data visualization.

**Components**:
- APIUsageChart
- ConversationTrafficChart (formerly ChatTrafficChart)
- UserActivityChart
- RealTimeMetrics

##### `features/auth/`
User authentication and profile management.

**Components**:
- LoginForm
- ModernLoginForm
- UserMenu
- UserProfile

##### `features/conversation/`
Chat/messaging interface (formerly `chat/`).

**Components**:
- ConversationArea (formerly ChatArea)
- ConversationHistory (formerly ChatHistory)
- ConversationInput (formerly ChatInput)
- ConversationSidebar (formerly Sidebar)
- MessageBubble
- TypingIndicator
- WelcomeScreen (formerly ChatWelcome)

##### `features/data-connections/`
Database connection management (merged from `connections/` and `database/`).

**Structure**:
```
data-connections/
├── forms/              # Connection configuration forms
│   ├── AthenaConnectionForm.tsx
│   ├── DatabaseConnectionForm.tsx
│   ├── DuckDBConnectionForm.tsx
│   └── PostgreSQLConnectionForm.tsx
├── schema/             # Schema exploration
│   ├── SchemaExplorer.tsx
│   ├── SchemaSelector.tsx
│   ├── CatalogSelector.tsx
│   ├── TableDiagram.tsx
│   └── TableList.tsx
└── [Main components]
    ├── ConnectionCard.tsx
    ├── ConnectionDashboard.tsx
    ├── ConnectionSelector.tsx
    ├── ConnectionWorkflow.tsx
    └── Text2SQLInterface.tsx
```

##### `features/file-manager/`
File upload and management (formerly `files/`).

**Components**:
- FileCard
- FileListItem
- FileUploadModal

##### `features/prompts/`
Prompt management for AI interactions.

**Components**:
- PromptCard
- PromptForm
- PromptManager

##### `features/workspace/`
Main workspace interface (formerly `main/`, removed "Julius" prefix).

**Components**:
- WorkspacePage (formerly JuliusMainPage)
- WorkspaceContent (formerly JuliusMainContent)
- WorkspaceSidebar (formerly JuliusSidebar)
- TemplateCards (formerly JuliusTemplateCards)

## 🔄 Migration from Old Structure

### Import Changes

#### Before:
```typescript
import { JuliusMainPage } from '@/components/features/main/JuliusMainPage';
import { ChatArea } from '@/components/features/chat/ChatArea';
import { ConnectionCard } from '@/components/features/connections/ConnectionCard';
import { APIUsageChart } from '@/components/charts/APIUsageChart';
```

#### After:
```typescript
import { WorkspacePage } from '@/components/features/workspace';
import { ConversationArea } from '@/components/features/conversation';
import { ConnectionCard } from '@/components/features/data-connections';
import { APIUsageChart } from '@/components/features/analytics';
```

### Component Naming Changes

| Old Name | New Name |
|----------|----------|
| JuliusMainPage | WorkspacePage |
| JuliusMainContent | WorkspaceContent |
| JuliusSidebar | WorkspaceSidebar |
| JuliusTemplateCards | TemplateCards |
| ChatArea | ConversationArea |
| ChatHistory | ConversationHistory |
| ChatInput | ConversationInput |
| ChatWelcome | WelcomeScreen |
| ChatTrafficChart | ConversationTrafficChart |

### Feature Name Changes

| Old Feature | New Feature | Reason |
|-------------|-------------|---------|
| `main/` | `workspace/` | Clearer purpose |
| `chat/` | `conversation/` | More professional |
| `connections/` + `database/` | `data-connections/` | Merged related features |
| `files/` | `file-manager/` | More descriptive |
| `charts/` | `analytics/` | Better organization |

## 📝 Best Practices

### 1. Component Placement

**Question**: Where should I put my new component?

**Decision Tree**:
1. **Is it a base UI element?** → `shared/ui/`
2. **Is it completely generic?** → `common/`
3. **Is it feature-specific?** → `features/{feature-name}/`
4. **Is it a layout component?** → `shared/layout/`
5. **Is it auth-related?** → `shared/auth/` or `features/auth/`

### 2. Naming Conventions

- Use PascalCase for component files: `ConnectionCard.tsx`
- Use descriptive names: `ConversationArea` not `ChatArea`
- Avoid abbreviations unless widely understood
- Remove product-specific prefixes (e.g., "Julius")
- Use domain language: "workspace" not "main"

### 3. Index Files

Each feature folder should have an `index.ts` for barrel exports:

```typescript
// features/conversation/index.ts
export { ConversationArea } from './ConversationArea';
export { ConversationHistory } from './ConversationHistory';
export { ConversationInput } from './ConversationInput';
// ... etc
```

### 4. Subdirectories

Use subdirectories when a feature has multiple component categories:

```
data-connections/
├── forms/          # Connection forms
├── schema/         # Schema exploration
└── [root]          # Main components
```

## 🚫 Deprecated Paths

The following paths are deprecated and will be removed:

- ❌ `@/components/features/main/`
- ❌ `@/components/features/chat/`
- ❌ `@/components/features/connections/`
- ❌ `@/components/features/database/`
- ❌ `@/components/features/files/`
- ❌ `@/components/charts/`

## ✅ Checklist for Adding New Components

- [ ] Choose appropriate directory (common/shared/features)
- [ ] Use clear, descriptive naming
- [ ] Add to feature's index.ts file
- [ ] Include TypeScript types
- [ ] Add JSDoc comments for complex components
- [ ] Follow existing patterns in the directory
- [ ] Update this README if adding new feature category

## 📚 Additional Resources

- See `COMPONENT_RESTRUCTURE.md` for detailed migration guide
- See `migration-map.ts` for import mapping
- See `migrate-components.sh` for migration script
