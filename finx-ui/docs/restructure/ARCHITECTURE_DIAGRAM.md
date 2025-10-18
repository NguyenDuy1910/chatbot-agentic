# FinX-UI Component Architecture Diagram

## Current State (Before Restructuring)

```
components/
│
├── charts/                          ❌ Top-level (should be in features)
│   ├── APIUsageChart.tsx
│   ├── ChatTrafficChart.tsx         ❌ "Chat" naming
│   ├── UserActivityChart.tsx
│   └── RealTimeMetrics.tsx
│
├── demo/                            ✓ OK - Development only
│
├── features/
│   ├── admin/                       ✓ OK
│   ├── auth/                        ✓ OK
│   │
│   ├── chat/                        ❌ Should be "conversation"
│   │   ├── ChatArea.tsx             ❌ Chat* prefix
│   │   ├── ChatHistory.tsx
│   │   ├── ChatInput.tsx
│   │   ├── ChatWelcome.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── Sidebar.tsx              ❌ Generic name
│   │   └── TypingIndicator.tsx
│   │
│   ├── connections/                 ❌ Split from database
│   │   ├── forms/
│   │   ├── ConnectionCard.tsx
│   │   ├── SchemaExplorer.tsx
│   │   └── ...
│   │
│   ├── database/                    ❌ Split from connections
│   │   ├── DatabaseConnectionForm.tsx
│   │   ├── Text2SQLInterface.tsx
│   │   └── ...
│   │
│   ├── files/                       ⚠️ Rename to "file-manager"
│   │
│   ├── main/                        ❌ "main" is unclear
│   │   ├── JuliusMainPage.tsx       ❌ "Julius" prefix unclear
│   │   ├── JuliusMainContent.tsx
│   │   ├── JuliusSidebar.tsx
│   │   └── JuliusTemplateCards.tsx
│   │
│   └── prompts/                     ✓ OK
│
└── shared/                          ✓ OK
    ├── auth/
    ├── layout/
    └── ui/
```

## New State (After Restructuring)

```
components/
│
├── common/                          ✨ NEW - Generic reusable
│   ├── cards/
│   ├── forms/
│   ├── lists/
│   └── modals/
│
├── demo/                            ✓ Same - Development only
│
├── features/                        ✨ Reorganized by domain
│   │
│   ├── admin/                       ✓ Same
│   │   ├── AdminDashboard.tsx
│   │   ├── UserManagement.tsx
│   │   └── ...
│   │
│   ├── analytics/                   ✨ MOVED from charts/
│   │   ├── APIUsageChart.tsx
│   │   ├── ConversationTrafficChart.tsx  ✨ Renamed
│   │   ├── UserActivityChart.tsx
│   │   └── RealTimeMetrics.tsx
│   │
│   ├── auth/                        ✓ Same
│   │   ├── LoginForm.tsx
│   │   ├── UserMenu.tsx
│   │   └── ...
│   │
│   ├── conversation/                ✨ RENAMED from chat/
│   │   ├── ConversationArea.tsx     ✨ Renamed
│   │   ├── ConversationHistory.tsx  ✨ Renamed
│   │   ├── ConversationInput.tsx    ✨ Renamed
│   │   ├── ConversationSidebar.tsx  ✨ Renamed
│   │   ├── WelcomeScreen.tsx        ✨ Renamed
│   │   ├── MessageBubble.tsx        ✓ Same
│   │   └── TypingIndicator.tsx      ✓ Same
│   │
│   ├── data-connections/            ✨ MERGED connections + database
│   │   ├── forms/                   ← From connections/forms + database
│   │   │   ├── AthenaConnectionForm.tsx
│   │   │   ├── DatabaseConnectionForm.tsx
│   │   │   ├── DuckDBConnectionForm.tsx
│   │   │   └── PostgreSQLConnectionForm.tsx
│   │   │
│   │   ├── schema/                  ← From connections/
│   │   │   ├── SchemaExplorer.tsx
│   │   │   ├── SchemaSelector.tsx
│   │   │   ├── CatalogSelector.tsx
│   │   │   ├── TableDiagram.tsx
│   │   │   └── TableList.tsx
│   │   │
│   │   └── [Root]                   ← From both features
│   │       ├── ConnectionCard.tsx
│   │       ├── ConnectionDashboard.tsx
│   │       ├── Text2SQLInterface.tsx
│   │       └── ...
│   │
│   ├── file-manager/                ✨ RENAMED from files/
│   │   ├── FileCard.tsx
│   │   ├── FileListItem.tsx
│   │   └── FileUploadModal.tsx
│   │
│   ├── prompts/                     ✓ Same
│   │   ├── PromptCard.tsx
│   │   ├── PromptForm.tsx
│   │   └── PromptManager.tsx
│   │
│   └── workspace/                   ✨ RENAMED from main/
│       ├── WorkspacePage.tsx        ✨ Renamed
│       ├── WorkspaceContent.tsx     ✨ Renamed
│       ├── WorkspaceSidebar.tsx     ✨ Renamed
│       └── TemplateCards.tsx        ✨ Renamed
│
└── shared/                          ✓ Same
    ├── auth/
    │   └── ProtectedRoute.tsx
    ├── layout/
    │   ├── AppHeader.tsx
    │   ├── AppSidebar.tsx
    │   ├── AppFooter.tsx
    │   └── ...
    └── ui/
        ├── Button.tsx
        ├── Input.tsx
        ├── Card.tsx
        └── ...
```

## Component Import Flow

### Before:
```typescript
// Imports scattered across different locations
import { JuliusMainPage } from '@/components/features/main/JuliusMainPage';
import { ChatArea, ChatInput } from '@/components/features/chat';
import { ConnectionCard } from '@/components/features/connections/ConnectionCard';
import { DatabaseManager } from '@/components/features/database/DatabaseManager';
import { APIUsageChart } from '@/components/charts/APIUsageChart';
```

### After:
```typescript
// Clean, organized imports by feature domain
import { WorkspacePage } from '@/components/features/workspace';
import { ConversationArea, ConversationInput } from '@/components/features/conversation';
import { ConnectionCard, DatabaseManager } from '@/components/features/data-connections';
import { APIUsageChart } from '@/components/features/analytics';
```

## Feature Organization Logic

```
┌─────────────────────────────────────────────────────────┐
│ Component Classification                                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Is it a base UI primitive?                             │
│  (Button, Input, Card)                                   │
│         ↓ YES                                            │
│    shared/ui/                                            │
│                                                           │
│  Is it completely generic?                              │
│  (Generic cards, form fields)                           │
│         ↓ YES                                            │
│    common/                                               │
│                                                           │
│  Is it infrastructure?                                   │
│  (Layout, auth wrappers)                                │
│         ↓ YES                                            │
│    shared/                                               │
│                                                           │
│  Is it feature-specific?                                │
│  (Business logic, domain components)                    │
│         ↓ YES                                            │
│    features/{domain}/                                    │
│                                                           │
│  Is it for testing only?                                │
│         ↓ YES                                            │
│    demo/                                                 │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Data Connections Merge Rationale

```
OLD STRUCTURE:
┌──────────────────┐       ┌──────────────────┐
│  connections/    │       │   database/      │
│                  │       │                  │
│ • Forms          │       │ • Forms          │  ❌ Duplicate
│ • Schema views   │       │ • SQL interface  │  ❌ Split logic
│ • Connection mgmt│       │ • DB cards       │  ❌ Confusing
└──────────────────┘       └──────────────────┘

NEW STRUCTURE:
┌─────────────────────────────────────────────┐
│        data-connections/                    │
│                                              │
│  ├── forms/         (All connection forms)  │  ✓ Unified
│  ├── schema/        (All schema exploration)│  ✓ Organized
│  └── [Root]         (Management & SQL)      │  ✓ Clear
└─────────────────────────────────────────────┘
```

## Naming Convention Changes

```
┌────────────────────────┬─────────────────────────┐
│ OLD NAME              │ NEW NAME                 │
├────────────────────────┼─────────────────────────┤
│ Julius*               │ Workspace*               │
│   ↓ Unclear branding  │   ↓ Clear purpose       │
│                        │                          │
│ Chat*                 │ Conversation*            │
│   ↓ Casual            │   ↓ Professional        │
│                        │                          │
│ main/                 │ workspace/               │
│   ↓ Generic           │   ↓ Descriptive         │
│                        │                          │
│ files/                │ file-manager/            │
│   ↓ Vague             │   ↓ Clear intent        │
│                        │                          │
│ connections/database/ │ data-connections/        │
│   ↓ Split             │   ↓ Unified             │
└────────────────────────┴─────────────────────────┘
```

## Benefits Visualization

```
BEFORE: 😕
├── Confusing naming (Julius, main)
├── Split features (connections/database)
├── Mixed structure (charts at root)
├── Unclear boundaries
└── Hard to navigate

AFTER: 😊
├── Clear naming (Workspace, Conversation)
├── Unified features (data-connections)
├── Consistent structure (all in features/)
├── Domain-driven organization
└── Easy to navigate
```

## Legend

```
✓ OK        - No changes needed
✨ NEW      - New location/name
❌ ISSUE    - Needs fixing
⚠️ WARNING  - Consider changing
← FROM      - Moved/merged from
```
