/**
 * Component Restructuring: Import Map
 * Use this to find and replace imports throughout the codebase
 */

export const IMPORT_MIGRATION_MAP = {
  // Workspace (formerly main/Julius)
  'JuliusMainPage': {
    oldPath: '@/components/features/main/JuliusMainPage',
    newPath: '@/components/features/workspace',
    newName: 'WorkspacePage',
  },
  'JuliusMainContent': {
    oldPath: '@/components/features/main/JuliusMainContent',
    newPath: '@/components/features/workspace',
    newName: 'WorkspaceContent',
  },
  'JuliusSidebar': {
    oldPath: '@/components/features/main/JuliusSidebar',
    newPath: '@/components/features/workspace',
    newName: 'WorkspaceSidebar',
  },
  'JuliusTemplateCards': {
    oldPath: '@/components/features/main/JuliusTemplateCards',
    newPath: '@/components/features/workspace',
    newName: 'TemplateCards',
  },

  // Conversation (formerly chat)
  'ChatArea': {
    oldPath: '@/components/features/chat/ChatArea',
    newPath: '@/components/features/conversation',
    newName: 'ConversationArea',
  },
  'ChatHistory': {
    oldPath: '@/components/features/chat/ChatHistory',
    newPath: '@/components/features/conversation',
    newName: 'ConversationHistory',
  },
  'ChatInput': {
    oldPath: '@/components/features/chat/ChatInput',
    newPath: '@/components/features/conversation',
    newName: 'ConversationInput',
  },
  'ChatWelcome': {
    oldPath: '@/components/features/chat/ChatWelcome',
    newPath: '@/components/features/conversation',
    newName: 'WelcomeScreen',
  },

  // Data Connections (merged connections + database)
  'ConnectionCard': {
    oldPath: '@/components/features/connections/ConnectionCard',
    newPath: '@/components/features/data-connections',
    newName: 'ConnectionCard',
  },
  'ConnectionDashboard': {
    oldPath: '@/components/features/connections/ConnectionDashboard',
    newPath: '@/components/features/data-connections',
    newName: 'ConnectionDashboard',
  },
  'AthenaConnectionForm': {
    oldPath: '@/components/features/connections/forms/AthenaConnectionForm',
    newPath: '@/components/features/data-connections/forms',
    newName: 'AthenaConnectionForm',
  },
  'DatabaseConnectionForm': {
    oldPath: [
      '@/components/features/connections/forms/DatabaseConnectionForm',
      '@/components/features/database/DatabaseConnectionForm',
    ],
    newPath: '@/components/features/data-connections/forms',
    newName: 'DatabaseConnectionForm',
  },
  'SchemaExplorer': {
    oldPath: '@/components/features/connections/SchemaExplorer',
    newPath: '@/components/features/data-connections/schema',
    newName: 'SchemaExplorer',
  },
  'Text2SQLInterface': {
    oldPath: '@/components/features/database/Text2SQLInterface',
    newPath: '@/components/features/data-connections',
    newName: 'Text2SQLInterface',
  },

  // Analytics (formerly charts)
  'APIUsageChart': {
    oldPath: '@/components/charts/APIUsageChart',
    newPath: '@/components/features/analytics',
    newName: 'APIUsageChart',
  },
  'ChatTrafficChart': {
    oldPath: '@/components/charts/ChatTrafficChart',
    newPath: '@/components/features/analytics',
    newName: 'ConversationTrafficChart',
  },
  'UserActivityChart': {
    oldPath: '@/components/charts/UserActivityChart',
    newPath: '@/components/features/analytics',
    newName: 'UserActivityChart',
  },
  'RealTimeMetrics': {
    oldPath: '@/components/charts/RealTimeMetrics',
    newPath: '@/components/features/analytics',
    newName: 'RealTimeMetrics',
  },
} as const;

/**
 * Find and Replace patterns for import statements
 * Use these with VS Code's Find & Replace (Ctrl/Cmd + Shift + H)
 */
export const FIND_REPLACE_PATTERNS = [
  // Workspace
  {
    find: "from '@/components/features/main/JuliusMainPage'",
    replace: "from '@/components/features/workspace'",
    note: "Also rename: JuliusMainPage → WorkspacePage",
  },
  {
    find: "from '@/components/features/main/JuliusMainContent'",
    replace: "from '@/components/features/workspace'",
    note: "Also rename: JuliusMainContent → WorkspaceContent",
  },
  {
    find: "from '@/components/features/main/JuliusSidebar'",
    replace: "from '@/components/features/workspace'",
    note: "Also rename: JuliusSidebar → WorkspaceSidebar",
  },
  {
    find: "from '@/components/features/main/JuliusTemplateCards'",
    replace: "from '@/components/features/workspace'",
    note: "Also rename: JuliusTemplateCards → TemplateCards",
  },

  // Conversation
  {
    find: "from '@/components/features/chat/ChatArea'",
    replace: "from '@/components/features/conversation'",
    note: "Also rename: ChatArea → ConversationArea",
  },
  {
    find: "from '@/components/features/chat/ChatHistory'",
    replace: "from '@/components/features/conversation'",
    note: "Also rename: ChatHistory → ConversationHistory",
  },
  {
    find: "from '@/components/features/chat/ChatInput'",
    replace: "from '@/components/features/conversation'",
    note: "Also rename: ChatInput → ConversationInput",
  },
  {
    find: "from '@/components/features/chat/ChatWelcome'",
    replace: "from '@/components/features/conversation'",
    note: "Also rename: ChatWelcome → WelcomeScreen",
  },

  // Data Connections
  {
    find: "from '@/components/features/connections/",
    replace: "from '@/components/features/data-connections/",
  },
  {
    find: "from '@/components/features/database/",
    replace: "from '@/components/features/data-connections/",
  },

  // Analytics
  {
    find: "from '@/components/charts/",
    replace: "from '@/components/features/analytics/",
  },
  {
    find: "ChatTrafficChart",
    replace: "ConversationTrafficChart",
  },
];

/**
 * Component name replacements
 * For renaming component names in JSX and exports
 */
export const COMPONENT_NAME_REPLACEMENTS = {
  'JuliusMainPage': 'WorkspacePage',
  'JuliusMainContent': 'WorkspaceContent',
  'JuliusSidebar': 'WorkspaceSidebar',
  'JuliusTemplateCards': 'TemplateCards',
  'ChatArea': 'ConversationArea',
  'ChatHistory': 'ConversationHistory',
  'ChatInput': 'ConversationInput',
  'ChatWelcome': 'WelcomeScreen',
  'ChatTrafficChart': 'ConversationTrafficChart',
} as const;

/**
 * Directories to be deprecated after migration
 */
export const DEPRECATED_DIRECTORIES = [
  'src/components/features/main',
  'src/components/features/chat',
  'src/components/features/connections',
  'src/components/features/database',
  'src/components/features/files',
  'src/components/charts',
] as const;
