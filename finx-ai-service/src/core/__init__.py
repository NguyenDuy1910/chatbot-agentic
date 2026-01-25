"""
Core abstractions and utilities for finx-ai-service.

This module provides the foundational abstractions and utilities used across
all graphs and pipelines in the application.
"""

from .base_graph import BaseGraph
from .base_state import BaseState, PipelineMetadata
from .node_registry import NodeRegistry, register_node

# Workflow State Management
from .workflow_state import (
    WorkflowState,
    SQLWorkflowState,
    IntentClassificationState,
    RetrievalWorkflowState,
    AssistanceWorkflowState,
    create_workflow_state,
    extend_state,
)

# Reusable Base Nodes
from .base_nodes import (
    BaseNode,
    LLMNode,
    JSONParseNode,
    ToolNode,
    ValidationNode,
    ConditionalNode,
    TransformNode,
    create_llm_node,
    create_tool_node,
    create_validation_node,
)

# Node Utilities & Decorators
from .node_utils import (
    # Decorators
    node,
    llm_node,
    validation_node,
    tool_node,
    # State utilities
    get_from_state,
    set_in_state,
    merge_states,
    extract_field,
    add_to_history,
    # Retry utilities
    should_retry,
    increment_retry,
    reset_retry,
    # Routing helpers
    create_conditional_router,
    route_by_field,
    route_by_validation,
)

try:
    from .providers.base import DocumentStoreProvider, EmbedderProvider, LLMProvider
except ImportError:
    # Providers are optional dependencies
    DocumentStoreProvider = None
    EmbedderProvider = None
    LLMProvider = None

__all__ = [
    # Base abstractions
    "BaseGraph",
    "BaseState",
    "PipelineMetadata",
    # Node registry
    "NodeRegistry",
    "register_node",
    # Workflow State Management
    "WorkflowState",
    "SQLWorkflowState",
    "IntentClassificationState",
    "RetrievalWorkflowState",
    "AssistanceWorkflowState",
    "create_workflow_state",
    "extend_state",
    # Reusable Base Nodes
    "BaseNode",
    "LLMNode",
    "JSONParseNode",
    "ToolNode",
    "ValidationNode",
    "ConditionalNode",
    "TransformNode",
    "create_llm_node",
    "create_tool_node",
    "create_validation_node",
    # Node Utilities & Decorators
    "node",
    "llm_node",
    "validation_node",
    "tool_node",
    "get_from_state",
    "set_in_state",
    "merge_states",
    "extract_field",
    "add_to_history",
    "should_retry",
    "increment_retry",
    "reset_retry",
    "create_conditional_router",
    "route_by_field",
    "route_by_validation",
    # Providers
    "LLMProvider",
    "EmbedderProvider",
    "DocumentStoreProvider",
]

