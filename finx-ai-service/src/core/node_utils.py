"""
Node Decorators and Utilities

This module provides decorators and utility functions to simplify
the creation and management of workflow nodes.
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from langfuse.decorators import observe as langfuse_observe

logger = logging.getLogger(__name__)


# ============================================================================
# NODE DECORATORS
# ============================================================================

def node(
    name: Optional[str] = None,
    track_timing: bool = True,
    track_errors: bool = True,
    observe: bool = True,
):
    """
    Decorator to convert a function into a workflow node.
    
    This decorator:
    - Sets current_step in state
    - Tracks execution timing
    - Handles errors gracefully
    - Integrates with Langfuse observability
    
    Usage:
        @node(name="my_node")
        async def my_node_func(state: Dict[str, Any]) -> Dict[str, Any]:
            # Your node logic here
            return state
    
    Args:
        name: Node name (defaults to function name)
        track_timing: Whether to track execution time
        track_errors: Whether to catch and log errors
        observe: Whether to use Langfuse observability
    """
    def decorator(func: Callable) -> Callable:
        node_name = name or func.__name__
        
        @functools.wraps(func)
        async def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            # Set current step
            state["current_step"] = node_name
            
            # Start timing
            start_time = time.time() if track_timing else None
            
            try:
                logger.info(f"Executing node: {node_name}")
                
                # Execute the actual function
                result = await func(state)
                
                # Track timing
                if track_timing and start_time:
                    duration_ms = (time.time() - start_time) * 1000
                    if "step_timings" not in result:
                        result["step_timings"] = {}
                    result["step_timings"][node_name] = duration_ms
                    logger.info(f"Node {node_name} completed in {duration_ms:.2f}ms")
                
                return result
                
            except Exception as e:
                if track_errors:
                    if "errors" not in state:
                        state["errors"] = []
                    state["errors"].append(f"{node_name}: {str(e)}")
                    logger.error(f"Error in node {node_name}: {e}", exc_info=True)
                    
                    # Track timing even for errors
                    if track_timing and start_time:
                        duration_ms = (time.time() - start_time) * 1000
                        if "step_timings" not in state:
                            state["step_timings"] = {}
                        state["step_timings"][node_name] = duration_ms
                    
                    return state
                else:
                    raise
        
        # Apply Langfuse observability if requested
        if observe:
            wrapper = langfuse_observe(name=node_name)(wrapper)
        
        return wrapper
    
    return decorator


def llm_node(
    name: Optional[str] = None,
    system_prompt_template: Optional[str] = None,
    user_prompt_template: Optional[str] = None,
    output_field: str = "llm_response",
    context_builder: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    response_format: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to create an LLM node from a simple function.
    
    The decorated function should return a dictionary with:
    - system_prompt: Optional system prompt
    - user_prompt: User prompt
    - context: Optional context for template rendering
    
    Usage:
        @llm_node(name="reasoning", output_field="reasoning_result")
        async def reasoning_node(state: Dict[str, Any]) -> Dict:
            return {
                "system_prompt": "You are a helpful assistant",
                "user_prompt": f"Analyze: {state['query']}",
            }
    
    Args:
        name: Node name
        system_prompt_template: Template path for system prompt
        user_prompt_template: Template path for user prompt
        output_field: Where to store LLM response
        context_builder: Function to build context for templates
        response_format: Optional response format specification
    """
    from src.workflows.common import clean_up_new_lines
    from src.workflows.prompts import render_prompt
    
    def decorator(func: Callable) -> Callable:
        node_name = name or func.__name__
        
        @functools.wraps(func)
        @node(name=node_name)
        async def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            # Get generator from context
            context = state.get("context", {})
            generator = context.get("generator")
            
            if not generator:
                logger.warning(f"{node_name}: No LLM generator found in context")
                state[output_field] = None
                return state
            
            # Get prompts from function
            prompt_info = await func(state)
            
            # Build prompts
            if user_prompt_template:
                prompt_context = context_builder(state) if context_builder else prompt_info.get("context", state)
                user_prompt = render_prompt(user_prompt_template, context=prompt_context)
            else:
                user_prompt = prompt_info.get("user_prompt", "")
            
            if system_prompt_template:
                prompt_context = context_builder(state) if context_builder else prompt_info.get("context", state)
                system_prompt = render_prompt(system_prompt_template, context=prompt_context)
            else:
                system_prompt = prompt_info.get("system_prompt")
            
            # Clean prompts
            user_prompt = clean_up_new_lines(user_prompt)
            if system_prompt:
                system_prompt = clean_up_new_lines(system_prompt)
            
            # Store prompts
            state["current_prompt"] = user_prompt
            state["current_system_prompt"] = system_prompt
            
            # Call LLM
            kwargs = {"prompt": user_prompt}
            if system_prompt:
                kwargs["system_prompt"] = system_prompt
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await generator(**kwargs)
            
            # Extract response
            if isinstance(response, dict):
                extracted = response.get("replies", [""])[0]
            else:
                extracted = str(response)
            
            # Store response
            state[output_field] = extracted
            
            # Track execution
            if "llm_executions" not in state:
                state["llm_executions"] = []
            state["llm_executions"].append({
                "node": node_name,
                "prompt": user_prompt,
                "system_prompt": system_prompt,
                "response": extracted,
                "timestamp": time.time(),
            })
            
            logger.info(f"{node_name}: LLM response stored ({len(extracted)} chars)")
            
            return state
        
        return wrapper
    
    return decorator


def validation_node(
    name: Optional[str] = None,
    output_field: str = "is_valid",
    errors_field: str = "validation_errors",
):
    """
    Decorator to create a validation node.
    
    The decorated function should return (is_valid, errors).
    
    Usage:
        @validation_node(name="sql_validation")
        async def validate_sql(state: Dict[str, Any]) -> tuple[bool, List[str]]:
            sql = state.get("generated_sql")
            if not sql:
                return False, ["No SQL generated"]
            # Validate SQL...
            return True, []
    
    Args:
        name: Node name
        output_field: Where to store validation result
        errors_field: Where to store validation errors
    """
    def decorator(func: Callable) -> Callable:
        node_name = name or func.__name__
        
        @functools.wraps(func)
        @node(name=node_name)
        async def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            # Run validation
            is_valid, errors = await func(state)
            
            # Store results
            state[output_field] = is_valid
            state[errors_field] = errors
            
            # Update validation info
            if "validation_info" not in state:
                state["validation_info"] = {}
            state["validation_info"]["is_valid"] = is_valid
            state["validation_info"]["validation_errors"] = errors
            state["validation_info"]["validation_timestamp"] = time.time()
            
            if is_valid:
                logger.info(f"{node_name}: Validation passed")
            else:
                logger.warning(f"{node_name}: Validation failed - {len(errors)} error(s)")
            
            return state
        
        return wrapper
    
    return decorator


def tool_node(
    name: Optional[str] = None,
    output_field: str = "tool_result",
    track_execution: bool = True,
):
    """
    Decorator to create a tool execution node.
    
    The decorated function should perform the tool logic and return the result.
    
    Usage:
        @tool_node(name="execute_sql", output_field="sql_results")
        async def execute_sql_tool(state: Dict[str, Any]) -> Any:
            sql = state.get("generated_sql")
            # Execute SQL...
            return results
    
    Args:
        name: Node name
        output_field: Where to store tool result
        track_execution: Whether to track execution info
    """
    def decorator(func: Callable) -> Callable:
        node_name = name or func.__name__
        
        @functools.wraps(func)
        @node(name=node_name)
        async def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            start_time = time.time()
            success = True
            error = None
            result = None
            
            try:
                # Execute tool
                result = await func(state)
                state[output_field] = result
                
            except Exception as e:
                success = False
                error = str(e)
                logger.error(f"{node_name}: Tool execution failed - {e}")
                state[output_field] = None
            
            # Track execution
            if track_execution:
                execution_time = (time.time() - start_time) * 1000
                
                if "tool_executions" not in state:
                    state["tool_executions"] = []
                
                state["tool_executions"].append({
                    "tool_name": node_name,
                    "tool_output": result,
                    "execution_time_ms": execution_time,
                    "success": success,
                    "error": error,
                    "timestamp": time.time(),
                })
            
            return state
        
        return wrapper
    
    return decorator


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_from_state(
    state: Dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    """
    Safely get a value from nested state.
    
    Usage:
        value = get_from_state(state, "context", "generator", default=None)
    
    Args:
        state: State dictionary
        *keys: Nested keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at the nested key or default
    """
    current = state
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def set_in_state(
    state: Dict[str, Any],
    value: Any,
    *keys: str,
) -> None:
    """
    Set a value in nested state, creating intermediate dicts as needed.
    
    Usage:
        set_in_state(state, "my_value", "nested", "key", "path")
    
    Args:
        state: State dictionary
        value: Value to set
        *keys: Nested keys to traverse
    """
    if not keys:
        return
    
    current = state
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def merge_states(
    base_state: Dict[str, Any],
    update_state: Dict[str, Any],
    merge_lists: bool = True,
) -> Dict[str, Any]:
    """
    Merge two states together.
    
    Args:
        base_state: Base state
        update_state: State with updates
        merge_lists: Whether to concatenate lists or replace them
        
    Returns:
        Merged state
    """
    result = base_state.copy()
    
    for key, value in update_state.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_states(result[key], value, merge_lists)
            elif isinstance(result[key], list) and isinstance(value, list) and merge_lists:
                result[key] = result[key] + value
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result


def extract_field(
    response: Any,
    field: str = "replies",
    index: int = 0,
    default: str = "",
) -> str:
    """
    Extract a field from LLM response.
    
    Args:
        response: LLM response
        field: Field to extract
        index: Index if field is a list
        default: Default value
        
    Returns:
        Extracted value
    """
    if isinstance(response, dict):
        value = response.get(field, [default])
        if isinstance(value, list) and len(value) > index:
            return value[index]
        return default
    return str(response)


def add_to_history(
    state: Dict[str, Any],
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Add a message to conversation history.
    
    Args:
        state: State dictionary
        role: Message role (user, assistant, system)
        content: Message content
        metadata: Optional metadata
    """
    if "histories" not in state:
        state["histories"] = []
    
    message = {
        "role": role,
        "content": content,
        "timestamp": time.time(),
    }
    
    if metadata:
        message["metadata"] = metadata
    
    state["histories"].append(message)


def should_retry(
    state: Dict[str, Any],
    max_retries: Optional[int] = None,
) -> bool:
    """
    Check if we should retry based on retry count.
    
    Args:
        state: State dictionary
        max_retries: Maximum retries (uses state's max_retries if not provided)
        
    Returns:
        Whether to retry
    """
    retry_count = state.get("retry_count", 0)
    max_retries = max_retries or state.get("max_retries", 3)
    return retry_count < max_retries


def increment_retry(state: Dict[str, Any]) -> None:
    """Increment retry counter."""
    state["retry_count"] = state.get("retry_count", 0) + 1


def reset_retry(state: Dict[str, Any]) -> None:
    """Reset retry counter."""
    state["retry_count"] = 0


# ============================================================================
# CONDITIONAL ROUTING HELPERS
# ============================================================================

def create_conditional_router(
    routes: Dict[str, Callable[[Dict[str, Any]], bool]],
    default: str = "default",
) -> Callable[[Dict[str, Any]], str]:
    """
    Create a conditional router function for graph edges.
    
    Usage:
        router = create_conditional_router({
            "valid": lambda state: state.get("is_valid", False),
            "invalid": lambda state: not state.get("is_valid", False),
        })
    
    Args:
        routes: Dictionary mapping route names to condition functions
        default: Default route if no conditions match
        
    Returns:
        Router function
    """
    def router(state: Dict[str, Any]) -> str:
        for route_name, condition_func in routes.items():
            if condition_func(state):
                return route_name
        return default
    
    return router


def route_by_field(
    field: str,
    value_map: Dict[Any, str],
    default: str = "default",
) -> Callable[[Dict[str, Any]], str]:
    """
    Create a router that routes based on a state field value.
    
    Usage:
        router = route_by_field("intent", {
            "TEXT_TO_SQL": "sql_generation",
            "GENERAL": "general_response",
        })
    
    Args:
        field: State field to check
        value_map: Mapping of field values to route names
        default: Default route
        
    Returns:
        Router function
    """
    def router(state: Dict[str, Any]) -> str:
        value = state.get(field)
        return value_map.get(value, default)
    
    return router


def route_by_validation(
    valid_route: str = "valid",
    invalid_route: str = "invalid",
    max_retries_route: str = "max_retries",
    valid_field: str = "is_valid",
    retry_field: str = "retry_count",
    max_retries_field: str = "max_retries",
) -> Callable[[Dict[str, Any]], str]:
    """
    Create a router for validation with retry logic.
    
    Args:
        valid_route: Route when validation passes
        invalid_route: Route when validation fails
        max_retries_route: Route when max retries exceeded
        valid_field: State field for validation result
        retry_field: State field for retry count
        max_retries_field: State field for max retries
        
    Returns:
        Router function
    """
    def router(state: Dict[str, Any]) -> str:
        is_valid = state.get(valid_field, False)
        retry_count = state.get(retry_field, 0)
        max_retries = state.get(max_retries_field, 3)
        
        if is_valid:
            return valid_route
        elif retry_count >= max_retries:
            return max_retries_route
        else:
            return invalid_route
    
    return router
