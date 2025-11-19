# Quick Reference: Component Restructuring

## 🎯 At a Glance

### What Changed?

| Feature | Old Location | New Location | Why? |
|---------|-------------|--------------|------|
| **Workspace** | `features/main/Julius*` | `features/workspace/Workspace*` | Clear naming, no branding prefix |
| **Conversation** | `features/chat/Chat*` | `features/conversation/Conversation*` | Professional terminology |
| **Data Connections** | `features/connections/` + `features/database/` | `features/data-connections/` | Unified related features |
| **Analytics** | `charts/` | `features/analytics/` | Consistent structure |
| **File Manager** | `features/files/` | `features/file-manager/` | More descriptive |

## 📦 Quick Import Reference

### Workspace Components
```typescript
// ❌ OLD
import { JuliusMainPage } from '@/components/features/main/JuliusMainPage';
import { JuliusMainContent } from '@/components/features/main/JuliusMainContent';

// ✅ NEW
import { WorkspacePage, WorkspaceContent } from '@/components/features/workspace';
```

### Conversation Components
```typescript
// ❌ OLD
import { ChatArea } from '@/components/features/chat/ChatArea';
import { ChatInput } from '@/components/features/chat/ChatInput';

// ✅ NEW
import { ConversationArea, ConversationInput } from '@/components/features/conversation';
```

### Data Connection Components
```typescript
// ❌ OLD
import { ConnectionCard } from '@/components/features/connections/ConnectionCard';
import { DatabaseManager } from '@/components/features/database/DatabaseManager';
import { AthenaConnectionForm } from '@/components/features/connections/forms/AthenaConnectionForm';

// ✅ NEW
import { 
  ConnectionCard, 
  DatabaseManager,
  AthenaConnectionForm 
} from '@/components/features/data-connections';
```

### Analytics Components
```typescript
// ❌ OLD
import { APIUsageChart } from '@/components/charts/APIUsageChart';
import { ChatTrafficChart } from '@/components/charts/ChatTrafficChart';

// ✅ NEW
import { 
  APIUsageChart, 
  ConversationTrafficChart 
} from '@/components/features/analytics';
```

## 🔄 Component Name Changes

| Old Name | New Name |
|----------|----------|
| `JuliusMainPage` | `WorkspacePage` |
| `JuliusMainContent` | `WorkspaceContent` |
| `JuliusSidebar` | `WorkspaceSidebar` |
| `JuliusTemplateCards` | `TemplateCards` |
| `ChatArea` | `ConversationArea` |
| `ChatHistory` | `ConversationHistory` |
| `ChatInput` | `ConversationInput` |
| `ChatWelcome` | `WelcomeScreen` |
| `ChatTrafficChart` | `ConversationTrafficChart` |
| `Sidebar` (in chat) | `ConversationSidebar` |

## 📂 New Directory Structure

```
components/
├── common/              ← Generic reusable components
├── shared/              ← Infrastructure (layout, auth, ui)
├── features/
│   ├── admin/
│   ├── analytics/       ← From charts/
│   ├── auth/
│   ├── conversation/    ← From chat/
│   ├── data-connections/← From connections/ + database/
│   │   ├── forms/
│   │   └── schema/
│   ├── file-manager/    ← From files/
│   ├── prompts/
│   └── workspace/       ← From main/
└── demo/
```

## 🚀 Migration Checklist

### For Each Component You're Updating:

- [ ] Update import path
- [ ] Update component name (if renamed)
- [ ] Update JSX usage (if renamed)
- [ ] Update any type references
- [ ] Test the component still works
- [ ] Check for any broken dependencies

### Example Migration:

**Before** (`MainPage.tsx`):
```typescript
import { JuliusMainPage } from '@/components/features/main/JuliusMainPage';

export default function MainPage() {
  return <JuliusMainPage />;
}
```

**After** (`MainPage.tsx`):
```typescript
import { WorkspacePage } from '@/components/features/workspace';

export default function MainPage() {
  return <WorkspacePage />;
}
```

## 🔍 Finding What Needs Updating

### Search for old imports:
```bash
# In finx-ui directory:

# Find workspace imports
grep -r "from '@/components/features/main" src/

# Find conversation imports
grep -r "from '@/components/features/chat" src/

# Find data connection imports
grep -r "from '@/components/features/connections" src/
grep -r "from '@/components/features/database" src/

# Find analytics imports
grep -r "from '@/components/charts" src/

# Find component usage
grep -r "JuliusMain\|<Chat\|ChatTrafficChart" src/ --include="*.tsx"
```

## 💡 Key Principles

1. **Domain-Driven Organization**: Group by business feature, not technical role
2. **Clear Naming**: Use descriptive names that match the domain
3. **No Branding in Code**: Remove product-specific prefixes (Julius, etc.)
4. **Professional Terminology**: "Conversation" not "Chat"
5. **Unified Features**: Merge related functionality

## 📝 Common Patterns

### Creating New Components

**Where should it go?**

```
┌─────────────────────────────────────┐
│ Is it a primitive UI element?      │
│ → shared/ui/                        │
├─────────────────────────────────────┤
│ Is it generic and reusable?        │
│ → common/                           │
├─────────────────────────────────────┤
│ Is it feature-specific?            │
│ → features/{feature-name}/          │
├─────────────────────────────────────┤
│ Is it for testing/demo?            │
│ → demo/                             │
└─────────────────────────────────────┘
```

### Naming New Components

- ✅ `ConversationArea` (descriptive + feature context)
- ✅ `WorkspaceContent` (clear purpose)
- ✅ `ConnectionCard` (domain term)
- ❌ `JuliusMainPage` (branded + vague)
- ❌ `ChatThing` (unclear)
- ❌ `MainComponent` (too generic)

## ⚠️ Important Notes

1. **Don't delete old files yet** - Wait until testing is complete
2. **Update imports gradually** - Test each change
3. **Keep demo components** - They're useful for development
4. **Document custom changes** - If you deviate from the plan

## 📞 Need Help?

See full documentation:
- `COMPONENT_RESTRUCTURE.md` - Complete guide
- `RESTRUCTURE_SUMMARY.md` - Current status
- `ARCHITECTURE_DIAGRAM.md` - Visual structure
- `src/components/README.md` - Organization principles
- `src/components/migration-map.ts` - Import mapping

---

**Last Updated:** $(date)
**Status:** Ready for component renaming and import updates
