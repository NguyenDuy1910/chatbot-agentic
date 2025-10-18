# Connection Type Modal - Quick Reference

## 📦 Components

### 1. ConnectionTypeModal
**Path**: `finx-ui/src/components/features/data-connections/ConnectionTypeModal.tsx`

**Purpose**: Display popup modal to select database type

**Props**:
```typescript
{
  isOpen: boolean;           // Control modal visibility
  onClose: () => void;       // Handler when modal closes
  onSelectType: (typeId: string) => void;  // Handler when user selects a database
}
```

**Usage**:
```tsx
<ConnectionTypeModal
  isOpen={isTypeModalOpen}
  onClose={onTypeModalClose}
  onSelectType={(typeId) => {
    console.log('Selected:', typeId);
    // Handle selection
  }}
/>
```

### 2. ConnectionWorkflowWithType
**Path**: `finx-ui/src/components/features/data-connections/ConnectionWorkflowWithType.tsx`

**Purpose**: Simplified workflow when database type is pre-selected

**Props**:
```typescript
{
  onBack?: () => void;                      // Back button handler
  preSelectedDatabaseType?: string | null;  // Pre-selected DB type
}
```

**Usage**:
```tsx
<ConnectionWorkflowWithType
  preSelectedDatabaseType="postgresql"
  onBack={() => setShowForm(false)}
/>
```

## 🎯 Database Types

| ID | Display Name | Icon | Color |
|----|--------------|------|-------|
| `postgresql` | PostgreSQL | Database | Blue → Purple |
| `athena` | Amazon Athena | Globe | Orange → Yellow |
| `duckdb` | DuckDB | BarChart | Green → Emerald |

## 🔄 State Flow

```
Dashboard (initial)
    ↓
User clicks "New Connection"
    ↓
isTypeModalOpen = true
    ↓
Modal displays
    ↓
User selects database (e.g., "postgresql")
    ↓
onSelectType("postgresql") called
    ↓
selectedConnectionType = "postgresql"
isTypeModalOpen = false
showForm = true
    ↓
ConnectionWorkflowWithType renders
    ↓
PostgreSQL form displays
    ↓
User fills form & submits
    ↓
Connection created
    ↓
Navigate to schema explorer or back to dashboard
```

## 🎨 CSS Classes & Styling

### Modal
```tsx
size="5xl"                              // Large modal
scrollBehavior="inside"                 // Scroll content inside
backdrop="bg-black/50 backdrop-blur-sm" // Blurred backdrop
```

### Cards
```tsx
className="group hover:shadow-2xl transition-all duration-300 
           border-2 border-transparent hover:border-primary-200 
           cursor-pointer hover:scale-[1.03]"
```

### Icons Container
```tsx
className={`p-6 rounded-2xl bg-gradient-to-br ${color} 
            text-white shadow-lg 
            group-hover:scale-110 transition-transform duration-300`}
```

## 📝 Code Snippets

### Opening Modal
```typescript
const { isOpen: isTypeModalOpen, onOpen: onTypeModalOpen, onClose: onTypeModalClose } = useDisclosure();

// In button onClick:
onTypeModalOpen();
```

### Handling Selection
```typescript
const [selectedConnectionType, setSelectedConnectionType] = useState<string | null>(null);

const handleSelectConnectionType = (typeId: string) => {
  setSelectedConnectionType(typeId);
  // Modal will close automatically via callback
};
```

### Conditional Rendering
```typescript
// In render:
if (showForm) {
  if (selectedConnectionType) {
    return <ConnectionWorkflowWithType preSelectedDatabaseType={selectedConnectionType} />;
  }
  return <ConnectionWorkflow forceNew={true} />;
}
```

## 🔧 Configuration

### Adding New Database Type

1. **Update ConnectionTypeModal.tsx**:
```typescript
const connectionTypes: ConnectionType[] = [
  // ... existing types
  {
    id: 'mysql',
    name: 'MySQL',
    description: 'Connect to MySQL databases',
    icon: <Database className="h-6 w-6" />,
    color: 'from-blue-400 to-cyan-500',
  },
];
```

2. **Update ConnectionWorkflowWithType.tsx**:
```typescript
type DatabaseType = 'postgresql' | 'athena' | 'duckdb' | 'mysql';

// Add form component:
{selectedDatabase === 'mysql' && (
  <MySQLConnectionForm
    onSuccess={handleConnectionCreated}
    onCancel={handleBackToDashboard}
  />
)}
```

3. **Create Form Component**:
   - Create `MySQLConnectionForm.tsx` in `forms/` directory
   - Follow pattern of existing forms

## 🐛 Troubleshooting

### Modal doesn't open
- Check `isTypeModalOpen` state
- Verify `onTypeModalOpen` is called
- Check console for errors

### Modal doesn't close after selection
- Ensure `onClose` is called in `onSelectType`
- Check `onTypeModalClose` is called

### Wrong form displays
- Verify `selectedConnectionType` value
- Check type matching logic in render condition
- Console.log the selected type

### Back button doesn't work
- Check `onBack` prop is passed
- Verify state reset in back handler
- Ensure all states are cleared

## 📊 State Variables Reference

```typescript
// In ConnectionDashboard.tsx:
const [showForm, setShowForm] = useState(false);
const [selectedConnectionType, setSelectedConnectionType] = useState<string | null>(null);
const { isOpen: isTypeModalOpen, onOpen: onTypeModalOpen, onClose: onTypeModalClose } = useDisclosure();

// States to reset on back:
setShowForm(false);
onFormClose();
setEditingConnection(null);
setSelectedTemplate(null);
setSelectedConnectionType(null);
```

## ⚡ Performance Tips

1. **Lazy Load Forms**: Only load form component when needed
2. **Memoize Cards**: Use `React.memo` for connection type cards
3. **Debounce Search**: If search gets slow, debounce input
4. **Virtual Scroll**: If many types, use virtual scrolling

## 🔐 Security Considerations

- Connection credentials handled by form components
- No sensitive data stored in modal state
- Forms handle validation and sanitization
- Backend validates all connection attempts

## 📱 Accessibility

- **Keyboard**: Tab through options, Enter to select
- **Screen Readers**: Proper ARIA labels on cards
- **Focus Management**: Focus trapped in modal when open
- **Color Contrast**: All text meets WCAG AA standards
- **ESC Key**: Closes modal
- **Focus Return**: Focus returns to trigger button on close

## 🌐 Internationalization (Future)

To add i18n support:
```typescript
import { useTranslation } from 'react-i18next';

const { t } = useTranslation();

// In JSX:
<h2>{t('connection.modal.title')}</h2>
```

## 📈 Analytics Events (Future)

Track these events:
- `modal_opened`: When modal opens
- `database_selected`: When user selects a type
- `modal_closed`: When modal closes
- `search_used`: When search is typed
- `connection_created`: When connection succeeds

```typescript
// Example:
analytics.track('database_selected', {
  database_type: typeId,
  timestamp: Date.now()
});
```
