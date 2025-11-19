# Workflows Architecture

This document describes the LangGraph-based workflow architecture for the finx-ai-service chatbot.

## Overview

The workflows module implements a modular, composable architecture using LangGraph's state graph pattern. Each workflow is organized as a feature-level graph that can be independently developed, tested, and composed into larger workflows.

## Folder Structure

```
src/workflows/
├── base.py                          # Base classes for feature graphs and nodes
├── common.py                        # Shared utility functions
├── __init__.py                      # Main exports
├── WORKFLOWS_ARCHITECTURE.md        # This file
│
├── intent_recommendation/           # Intent classification and recommendations
│   ├── graph.py                     # Main graph definition
│   ├── state.py                     # State schema
│   ├── nodes/                       # Processing nodes
│   │   ├── classification.py        # Intent classification node
│   │   ├── questions.py             # Question recommendation node
│   │   ├── relationships.py         # Relationship recommendation node
│   │   └── semantics.py             # Semantics description node
│   ├── subgraphs/                   # Optional subgraph implementations
│   ├── demo.py                      # Demo script
│   └── simple_example.py            # Simple usage example
│
├── sql_processing/                  # SQL generation and processing
│   ├── graph.py                     # Main graph definition
│   ├── state.py                     # State schema
│   ├── nodes/                       # Processing nodes
│   │   ├── reasoning.py             # SQL reasoning node
│   │   ├── generation.py            # SQL generation node
│   │   ├── validation.py            # SQL validation node
│   │   ├── correction.py            # SQL correction node
│   │   ├── diagnosis.py             # SQL diagnosis node
│   │   ├── regeneration.py          # SQL regeneration node
│   │   ├── extraction.py            # Tables extraction node
│   │   ├── question.py              # Question generation node
│   │   └── answer.py                # Answer processing node
│   └── subgraphs/                   # Optional subgraph implementations
│
├── assistance_visualization/        # User assistance and chart visualization
│   ├── graph.py                     # Main graph definition
│   ├── state.py                     # State schema
│   ├── nodes/                       # Processing nodes
│   │   ├── data_assistance.py       # Data assistance node
│   │   ├── user_guide_assistance.py # User guide assistance node
│   │   ├── misleading_assistance.py # Misleading query assistance node
│   │   ├── chart_generation.py      # Chart generation node
│   │   └── chart_adjustment.py      # Chart adjustment node
│   └── subgraphs/                   # Optional subgraph implementations
│
└── orchestrator/                    # Master orchestrator
    ├── graph.py                     # Master orchestrator graph
    ├── state.py                     # Orchestrator state schema
    ├── __init__.py                  # Exports
    └── demo.py                      # Demo script
```

## Architecture Patterns

### 1. Base Classes

**FeatureGraph**: Abstract base class for all feature-level graphs
- Requires implementation of `get_state_schema()`, `_add_nodes()`, `_add_edges()`
- Handles graph building and compilation
- Provides common functionality for all graphs

**FeatureNode**: Abstract base class for individual processing nodes
- Defines the interface for node implementations
- Ensures consistent node behavior across the system

### 2. State Management

Each graph has a TypedDict-based state schema that extends BaseState:
- Defines all data flowing through the graph
- Enables type-safe state management
- Supports conditional routing based on state values

### 3. Node Organization

Nodes are organized in a `nodes/` subdirectory within each feature:
- Each node is a separate module with a single responsibility
- Nodes are imported and registered in the graph
- Nodes can be reused across different graphs

### 4. Conditional Routing

Graphs use conditional edges for intelligent routing:
- Intent-based routing in Intent & Recommendation graph
- Validation-based routing in SQL Processing graph
- Assistance type routing in Assistance & Visualization graph

## Main Workflows

### 1. Intent & Recommendation Graph

**Purpose**: Classify user intent and provide relevant recommendations

**Workflow**:
1. Intent Classification - Classify query as TEXT_TO_SQL, GENERAL, USER_GUIDE, or MISLEADING_QUERY
2. Route by Intent:
   - TEXT_TO_SQL → Question Recommendation
   - GENERAL → Semantics Description → Relationship Recommendation
   - USER_GUIDE → Question Recommendation
   - MISLEADING_QUERY → End

**Key Features**:
- Intent-based conditional routing
- Multiple recommendation types
- Graceful handling of all intent types

### 2. SQL Processing Graph

**Purpose**: Generate, validate, and correct SQL queries

**Workflow**:
1. Check if follow-up question
   - Yes: Follow-up SQL Reasoning → Follow-up SQL Generation
   - No: SQL Reasoning → SQL Generation
2. SQL Validation
   - Valid: SQL Tables Extraction → SQL Question → SQL Answer → End
   - Invalid: SQL Diagnosis → SQL Correction → Retry
   - Max Retries: SQL Regeneration

**Key Features**:
- Follow-up question handling
- SQL validation and correction with retry loops
- SQL regeneration when correction fails
- Answer generation from SQL results

### 3. Assistance & Visualization Graph

**Purpose**: Provide user assistance and generate chart visualizations

**Workflow**:
1. Route by Intent:
   - GENERAL → Data Assistance
   - USER_GUIDE → User Guide Assistance
   - MISLEADING_QUERY → Misleading Assistance
   - TEXT_TO_SQL (with visualization) → Chart Generation
2. Chart Adjustment (if needed)
   - Check if adjustment instructions provided
   - Yes: Chart Adjustment
   - No: End

**Key Features**:
- Intent-based routing to different assistance types
- Streaming responses for assistance nodes
- Chart generation and adjustment
- Graceful handling of all intent types

### 4. Master Orchestrator Graph

**Purpose**: Coordinate all three sub-graphs for complete workflow

**Workflow**:
1. Initialize Session
2. Intent Classification & Recommendation
3. SQL Processing (if TEXT_TO_SQL)
4. Assistance & Visualization
5. Session Cleanup

**Key Features**:
- Coordinates three independent sub-graphs
- Manages session state and context
- Handles error propagation
- Provides analytics and logging

## Creating New Features

To add a new feature workflow:

1. Create a new directory under `src/workflows/`
2. Create `state.py` with TypedDict state schema
3. Create `nodes/` directory with individual node modules
4. Create `graph.py` implementing FeatureGraph
5. Export graph and state from `__init__.py`
6. Register in orchestrator if needed

## Composing Workflows

Workflows are composed by:
1. Creating instances of sub-graphs
2. Invoking them with appropriate input state
3. Merging results back to parent state
4. Continuing with next workflow step

See `orchestrator/graph.py` for composition examples.

## Common Utilities

The `common.py` module provides shared utilities:
- `get_engine_supported_data_type()` - Data type conversion
- `build_table_ddl()` - DDL generation
- `retrieve_metadata()` - Metadata retrieval
- `clean_up_new_lines()` - Text cleaning

## Running Workflows

### Direct Graph Execution

```python
from src.workflows.intent_recommendation import create_initial_intent_recommendation_state
from src.workflows.intent_recommendation.graph import create_intent_recommendation_graph

graph = create_intent_recommendation_graph()
state = create_initial_intent_recommendation_state(query="your query")
result = graph.app.invoke(state)
```

### Async Execution

```python
result = await graph.app.ainvoke(state)
```

### Demo Scripts

Each workflow includes demo scripts:
- `demo.py` - Comprehensive examples with different scenarios
- `simple_example.py` - Minimal getting started example

Run demos with:
```bash
python -m src.workflows.intent_recommendation.demo
python -m src.workflows.orchestrator.demo
```

## Testing

Each workflow should have corresponding tests that:
- Test individual nodes
- Test graph routing logic
- Test state transformations
- Test error handling

## Migration Notes

This architecture replaces the previous Haystack-based implementation:
- Haystack pipelines → LangGraph state graphs
- Haystack components → LangGraph nodes
- Haystack document stores → State-based data flow
- Haystack retrievers → Custom retrieval nodes

