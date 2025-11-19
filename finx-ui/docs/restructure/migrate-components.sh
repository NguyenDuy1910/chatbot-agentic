#!/bin/bash

# FinX-UI Component Restructuring Migration Script
# This script helps migrate components to the new structure

set -e

BASE_DIR="/Users/duynguyen/Documents/vikki-bank-code/ai-team/chatbot-agentic/finx-ui/src/components"
FEATURES_DIR="$BASE_DIR/features"

echo "🚀 Starting FinX-UI Component Restructuring..."
echo ""

# Phase 1: Migrate Workspace Components (from main/)
echo "📦 Phase 1: Migrating Workspace Components..."
if [ -d "$FEATURES_DIR/main" ]; then
  # Copy files with new names
  [ -f "$FEATURES_DIR/main/JuliusMainPage.tsx" ] && cp "$FEATURES_DIR/main/JuliusMainPage.tsx" "$FEATURES_DIR/workspace/WorkspacePage.tsx"
  [ -f "$FEATURES_DIR/main/JuliusMainContent.tsx" ] && cp "$FEATURES_DIR/main/JuliusMainContent.tsx" "$FEATURES_DIR/workspace/WorkspaceContent.tsx"
  [ -f "$FEATURES_DIR/main/JuliusSidebar.tsx" ] && cp "$FEATURES_DIR/main/JuliusSidebar.tsx" "$FEATURES_DIR/workspace/WorkspaceSidebar.tsx"
  [ -f "$FEATURES_DIR/main/JuliusTemplateCards.tsx" ] && cp "$FEATURES_DIR/main/JuliusTemplateCards.tsx" "$FEATURES_DIR/workspace/TemplateCards.tsx"
  echo "  ✅ Workspace components copied"
else
  echo "  ⚠️  features/main/ directory not found"
fi

# Phase 2: Migrate Conversation Components (from chat/)
echo "📦 Phase 2: Migrating Conversation Components..."
if [ -d "$FEATURES_DIR/chat" ]; then
  [ -f "$FEATURES_DIR/chat/ChatArea.tsx" ] && cp "$FEATURES_DIR/chat/ChatArea.tsx" "$FEATURES_DIR/conversation/ConversationArea.tsx"
  [ -f "$FEATURES_DIR/chat/ChatHistory.tsx" ] && cp "$FEATURES_DIR/chat/ChatHistory.tsx" "$FEATURES_DIR/conversation/ConversationHistory.tsx"
  [ -f "$FEATURES_DIR/chat/ChatInput.tsx" ] && cp "$FEATURES_DIR/chat/ChatInput.tsx" "$FEATURES_DIR/conversation/ConversationInput.tsx"
  [ -f "$FEATURES_DIR/chat/Sidebar.tsx" ] && cp "$FEATURES_DIR/chat/Sidebar.tsx" "$FEATURES_DIR/conversation/ConversationSidebar.tsx"
  [ -f "$FEATURES_DIR/chat/ChatWelcome.tsx" ] && cp "$FEATURES_DIR/chat/ChatWelcome.tsx" "$FEATURES_DIR/conversation/WelcomeScreen.tsx"
  [ -f "$FEATURES_DIR/chat/MessageBubble.tsx" ] && cp "$FEATURES_DIR/chat/MessageBubble.tsx" "$FEATURES_DIR/conversation/MessageBubble.tsx"
  [ -f "$FEATURES_DIR/chat/TypingIndicator.tsx" ] && cp "$FEATURES_DIR/chat/TypingIndicator.tsx" "$FEATURES_DIR/conversation/TypingIndicator.tsx"
  echo "  ✅ Conversation components copied"
else
  echo "  ⚠️  features/chat/ directory not found"
fi

# Phase 3: Migrate Data Connection Components
echo "📦 Phase 3: Migrating Data Connection Components..."

# Copy connection forms
if [ -d "$FEATURES_DIR/connections/forms" ]; then
  cp "$FEATURES_DIR/connections/forms/"*.tsx "$FEATURES_DIR/data-connections/forms/" 2>/dev/null || true
  echo "  ✅ Connection forms copied"
fi

# Copy schema components
if [ -d "$FEATURES_DIR/connections" ]; then
  [ -f "$FEATURES_DIR/connections/SchemaExplorer.tsx" ] && cp "$FEATURES_DIR/connections/SchemaExplorer.tsx" "$FEATURES_DIR/data-connections/schema/"
  [ -f "$FEATURES_DIR/connections/SchemaSelector.tsx" ] && cp "$FEATURES_DIR/connections/SchemaSelector.tsx" "$FEATURES_DIR/data-connections/schema/"
  [ -f "$FEATURES_DIR/connections/CatalogSelector.tsx" ] && cp "$FEATURES_DIR/connections/CatalogSelector.tsx" "$FEATURES_DIR/data-connections/schema/"
  [ -f "$FEATURES_DIR/connections/TableDiagram.tsx" ] && cp "$FEATURES_DIR/connections/TableDiagram.tsx" "$FEATURES_DIR/data-connections/schema/"
  [ -f "$FEATURES_DIR/connections/TableList.tsx" ] && cp "$FEATURES_DIR/connections/TableList.tsx" "$FEATURES_DIR/data-connections/schema/"
  [ -f "$FEATURES_DIR/connections/AthenaSchemaExplorer.tsx" ] && cp "$FEATURES_DIR/connections/AthenaSchemaExplorer.tsx" "$FEATURES_DIR/data-connections/schema/"
  echo "  ✅ Schema components copied"
fi

# Copy main connection components
if [ -d "$FEATURES_DIR/connections" ]; then
  [ -f "$FEATURES_DIR/connections/ConnectionCard.tsx" ] && cp "$FEATURES_DIR/connections/ConnectionCard.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/connections/ConnectionDashboard.tsx" ] && cp "$FEATURES_DIR/connections/ConnectionDashboard.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/connections/ConnectionSelector.tsx" ] && cp "$FEATURES_DIR/connections/ConnectionSelector.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/connections/ConnectionStatsGrid.tsx" ] && cp "$FEATURES_DIR/connections/ConnectionStatsGrid.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/connections/ConnectionWorkflow.tsx" ] && cp "$FEATURES_DIR/connections/ConnectionWorkflow.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/connections/SavedConnectionsList.tsx" ] && cp "$FEATURES_DIR/connections/SavedConnectionsList.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/connections/QuickConnectionReuse.tsx" ] && cp "$FEATURES_DIR/connections/QuickConnectionReuse.tsx" "$FEATURES_DIR/data-connections/"
  echo "  ✅ Main connection components copied"
fi

# Copy database components
if [ -d "$FEATURES_DIR/database" ]; then
  [ -f "$FEATURES_DIR/database/Text2SQLInterface.tsx" ] && cp "$FEATURES_DIR/database/Text2SQLInterface.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/database/DatabaseConnectionForm.tsx" ] && cp "$FEATURES_DIR/database/DatabaseConnectionForm.tsx" "$FEATURES_DIR/data-connections/forms/"
  [ -f "$FEATURES_DIR/database/DatabaseConnectionCard.tsx" ] && cp "$FEATURES_DIR/database/DatabaseConnectionCard.tsx" "$FEATURES_DIR/data-connections/"
  [ -f "$FEATURES_DIR/database/DatabaseManager.tsx" ] && cp "$FEATURES_DIR/database/DatabaseManager.tsx" "$FEATURES_DIR/data-connections/"
  echo "  ✅ Database components copied"
fi

# Phase 4: Migrate Analytics Components (from charts/)
echo "📦 Phase 4: Migrating Analytics Components..."
if [ -d "$BASE_DIR/charts" ]; then
  [ -f "$BASE_DIR/charts/APIUsageChart.tsx" ] && cp "$BASE_DIR/charts/APIUsageChart.tsx" "$FEATURES_DIR/analytics/"
  [ -f "$BASE_DIR/charts/ChatTrafficChart.tsx" ] && cp "$BASE_DIR/charts/ChatTrafficChart.tsx" "$FEATURES_DIR/analytics/ConversationTrafficChart.tsx"
  [ -f "$BASE_DIR/charts/UserActivityChart.tsx" ] && cp "$BASE_DIR/charts/UserActivityChart.tsx" "$FEATURES_DIR/analytics/"
  [ -f "$BASE_DIR/charts/RealTimeMetrics.tsx" ] && cp "$BASE_DIR/charts/RealTimeMetrics.tsx" "$FEATURES_DIR/analytics/"
  echo "  ✅ Analytics components copied"
else
  echo "  ⚠️  charts/ directory not found"
fi

# Phase 5: Create feature index files
echo "📦 Phase 5: Creating feature index files..."
# This will be done with TypeScript later

echo ""
echo "✅ Migration Phase 1 Complete!"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "  1. Update component imports in the copied files"
echo "  2. Rename component class names (e.g., JuliusMainPage → WorkspacePage)"
echo "  3. Update all pages that import these components"
echo "  4. Test all functionality"
echo "  5. Once verified, delete old directories"
echo ""
echo "📝 See COMPONENT_RESTRUCTURE.md for detailed migration guide"
