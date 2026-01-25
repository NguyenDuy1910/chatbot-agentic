"""
Reusable Base Nodes for LangGraph Workflows

This module provides a collection of reusable node classes that can be used
across different workflows. Each node is designed to perform a specific type
of operation (LLM call, tool execution, retrieval, validation, etc.).
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

import orjson
from langfuse.decorators import observe

from src.workflows.common import clean_up_new_lines
from src.workflows.prompts import render_prompt

logger = logging.getLogger(__name__)


# ============================================================================
# ABSTRACT BASE NODE
# ============================================================================

class BaseNode(ABC):
    """
    Abstract base class for all workflow nodes.
    
    All nodes should inherit from this class and implement the execute method.
    """
    
    def __init__(self, name: str, node_type: str = "generic"):
        """
        Initialize base node.
        
        Args:
            name: Name of the node (used for logging and tracking)
            node_type: Type of node (llm, tool, retrieval, etc.)
        """
        self.name = name
        self.node_type = node_type
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node logic.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        pass
    
    def _update_step_timing(self, state: Dict[str, Any], duration_ms: float) -> None:
        """Record execution time for this step."""
        if "step_timings" not in state:
            state["step_timings"] = {}
        state["step_timings"][self.name] = duration_ms
    
    def _add_error(self, state: Dict[str, Any], error_msg: str) -> None:
        """Add error to state."""
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"{self.name}: {error_msg}")
        self.logger.error(error_msg)
    
    def _add_warning(self, state: Dict[str, Any], warning_msg: str) -> None:
        """Add warning to state."""
        if "warnings" not in state:
            state["warnings"] = []
        state["warnings"].append(f"{self.name}: {warning_msg}")
        self.logger.warning(warning_msg)
    
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the node (wrapper around execute with timing and error handling).
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = time.time()
        state["current_step"] = self.name
        
        try:
            self.logger.info(f"Executing node: {self.name}")
            result = await self.execute(state)
            duration_ms = (time.time() - start_time) * 1000
            self._update_step_timing(result, duration_ms)
            self.logger.info(f"Node {self.name} completed in {duration_ms:.2f}ms")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._update_step_timing(state, duration_ms)
            self._add_error(state, f"Execution failed: {str(e)}")
            self.logger.exception(f"Error in node {self.name}")
            return state


# ============================================================================
# LLM NODE
# ============================================================================

class LLMNode(BaseNode):
    """
    Node for executing LLM calls with prompt templates.
    
    This node handles:
    - Prompt template rendering
    - LLM execution
    - Response parsing
    - Execution tracking
    """
    
    def __init__(
        self,
        name: str,
        system_prompt_template: Optional[str] = None,
        user_prompt_template: Optional[str] = None,
        system_prompt_text: Optional[str] = None,
        user_prompt_text: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        extract_field: Optional[str] = None,
        output_field: str = "llm_response",
        context_builder: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        """
        Initialize LLM node.
        
        Args:
            name: Node name
            system_prompt_template: Path to system prompt Jinja2 template
            user_prompt_template: Path to user prompt Jinja2 template
            system_prompt_text: Direct system prompt text (alternative to template)
            user_prompt_text: Direct user prompt text (alternative to template)
            response_format: Optional response format specification
            extract_field: Field to extract from response (e.g., "replies")
            output_field: State field to store the response
            context_builder: Optional function to build context for prompt rendering
        """
        super().__init__(name, "llm")
        self.system_prompt_template = system_prompt_template
        self.user_prompt_template = user_prompt_template
        self.system_prompt_text = system_prompt_text
        self.user_prompt_text = user_prompt_text
        self.response_format = response_format
        self.extract_field = extract_field
        self.output_field = output_field
        self.context_builder = context_builder
    
    def _build_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for prompt rendering."""
        if self.context_builder:
            return self.context_builder(state)
        return state
    
    def _render_prompts(self, state: Dict[str, Any]) -> tuple[Optional[str], str]:
        """Render system and user prompts."""
        context = self._build_context(state)
        
        # Render system prompt
        if self.system_prompt_template:
            system_prompt = render_prompt(self.system_prompt_template, context=context)
        elif self.system_prompt_text:
            system_prompt = self.system_prompt_text
        else:
            system_prompt = None
        
        # Render user prompt
        if self.user_prompt_template:
            user_prompt = render_prompt(self.user_prompt_template, context=context)
        elif self.user_prompt_text:
            user_prompt = self.user_prompt_text
        else:
            raise ValueError(f"Node {self.name}: No user prompt template or text provided")
        
        # Clean up newlines
        user_prompt = clean_up_new_lines(user_prompt)
        if system_prompt:
            system_prompt = clean_up_new_lines(system_prompt)
        
        return system_prompt, user_prompt
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LLM call."""
        # Get generator from context
        context = state.get("context", {})
        generator = context.get("generator")
        
        if not generator:
            self._add_error(state, "No LLM generator found in context")
            return state
        
        try:
            # Render prompts
            system_prompt, user_prompt = self._render_prompts(state)
            
            # Store prompts in state
            state["current_system_prompt"] = system_prompt
            state["current_prompt"] = user_prompt
            
            # Call LLM
            kwargs = {
                "prompt": user_prompt,
            }
            if system_prompt:
                kwargs["system_prompt"] = system_prompt
            if self.response_format:
                kwargs["response_format"] = self.response_format
            
            response = await generator(**kwargs)
            
            # Extract response
            if isinstance(response, dict):
                if self.extract_field:
                    extracted = response.get(self.extract_field, [""])[0]
                else:
                    extracted = response.get("replies", [""])[0]
            else:
                extracted = str(response)
            
            # Store response
            state[self.output_field] = extracted
            
            # Track LLM execution
            if "llm_executions" not in state:
                state["llm_executions"] = []
            
            state["llm_executions"].append({
                "node": self.name,
                "prompt": user_prompt,
                "system_prompt": system_prompt,
                "response": extracted,
                "timestamp": time.time(),
            })
            
            self.logger.info(f"LLM response stored in '{self.output_field}': {len(extracted)} chars")
            
        except Exception as e:
            self._add_error(state, f"LLM execution failed: {str(e)}")
        
        return state


# ============================================================================
# JSON PARSING NODE
# ============================================================================

class JSONParseNode(BaseNode):
    """
    Node for parsing JSON responses from LLM.
    
    This node takes a string response and parses it as JSON.
    """
    
    def __init__(
        self,
        name: str,
        input_field: str = "llm_response",
        output_field: str = "parsed_response",
        default_value: Any = None,
        required_fields: Optional[List[str]] = None,
    ):
        """
        Initialize JSON parse node.
        
        Args:
            name: Node name
            input_field: State field containing JSON string
            output_field: State field to store parsed JSON
            default_value: Default value if parsing fails
            required_fields: List of required fields in parsed JSON
        """
        super().__init__(name, "json_parse")
        self.input_field = input_field
        self.output_field = output_field
        self.default_value = default_value
        self.required_fields = required_fields or []
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON from input field."""
        try:
            json_string = state.get(self.input_field, "")
            
            if not json_string:
                self._add_warning(state, f"No content in '{self.input_field}'")
                state[self.output_field] = self.default_value
                return state
            
            # Parse JSON
            parsed = orjson.loads(json_string)
            
            # Validate required fields
            if self.required_fields:
                missing_fields = [field for field in self.required_fields if field not in parsed]
                if missing_fields:
                    self._add_warning(state, f"Missing required fields: {missing_fields}")
            
            state[self.output_field] = parsed
            self.logger.info(f"Successfully parsed JSON into '{self.output_field}'")
            
        except Exception as e:
            self._add_error(state, f"JSON parsing failed: {str(e)}")
            state[self.output_field] = self.default_value
        
        return state


# ============================================================================
# TOOL EXECUTION NODE
# ============================================================================

class ToolNode(BaseNode):
    """
    Node for executing tools/functions.
    
    This node handles:
    - Tool input preparation
    - Tool execution
    - Result storage
    - Error handling
    """
    
    def __init__(
        self,
        name: str,
        tool_func: Callable,
        input_builder: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        output_field: str = "tool_result",
        track_execution: bool = True,
    ):
        """
        Initialize tool node.
        
        Args:
            name: Node name
            tool_func: Tool function to execute
            input_builder: Function to build tool inputs from state
            output_field: State field to store tool result
            track_execution: Whether to track execution in state
        """
        super().__init__(name, "tool")
        self.tool_func = tool_func
        self.input_builder = input_builder
        self.output_field = output_field
        self.track_execution = track_execution
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool."""
        try:
            # Build tool inputs
            if self.input_builder:
                tool_input = self.input_builder(state)
            else:
                tool_input = {}
            
            # Execute tool
            start_time = time.time()
            result = await self.tool_func(**tool_input)
            execution_time = (time.time() - start_time) * 1000
            
            # Store result
            state[self.output_field] = result
            
            # Track execution
            if self.track_execution:
                if "tool_executions" not in state:
                    state["tool_executions"] = []
                
                state["tool_executions"].append({
                    "tool_name": self.name,
                    "tool_input": tool_input,
                    "tool_output": result,
                    "execution_time_ms": execution_time,
                    "success": True,
                    "error": None,
                })
            
            self.logger.info(f"Tool executed successfully in {execution_time:.2f}ms")
            
        except Exception as e:
            self._add_error(state, f"Tool execution failed: {str(e)}")
            
            if self.track_execution:
                if "tool_executions" not in state:
                    state["tool_executions"] = []
                
                state["tool_executions"].append({
                    "tool_name": self.name,
                    "tool_input": tool_input if 'tool_input' in locals() else {},
                    "tool_output": None,
                    "execution_time_ms": 0,
                    "success": False,
                    "error": str(e),
                })
        
        return state


# ============================================================================
# VALIDATION NODE
# ============================================================================

class ValidationNode(BaseNode):
    """
    Node for validating data against rules.
    
    This node handles:
    - Rule-based validation
    - Custom validation functions
    - Validation result tracking
    """
    
    def __init__(
        self,
        name: str,
        validation_func: Callable[[Dict[str, Any]], tuple[bool, List[str]]],
        input_field: Optional[str] = None,
        output_field: str = "is_valid",
        errors_field: str = "validation_errors",
    ):
        """
        Initialize validation node.
        
        Args:
            name: Node name
            validation_func: Function that returns (is_valid, errors)
            input_field: Optional specific field to validate
            output_field: State field to store validation result
            errors_field: State field to store validation errors
        """
        super().__init__(name, "validation")
        self.validation_func = validation_func
        self.input_field = input_field
        self.output_field = output_field
        self.errors_field = errors_field
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation."""
        try:
            # Get data to validate
            if self.input_field:
                data = state.get(self.input_field)
            else:
                data = state
            
            # Run validation
            is_valid, errors = self.validation_func(data)
            
            # Store results
            state[self.output_field] = is_valid
            state[self.errors_field] = errors
            
            # Update validation info
            if "validation_info" not in state:
                state["validation_info"] = {}
            
            state["validation_info"]["is_valid"] = is_valid
            state["validation_info"]["validation_errors"] = errors
            state["validation_info"]["validation_timestamp"] = time.time()
            
            if is_valid:
                self.logger.info("Validation passed")
            else:
                self.logger.warning(f"Validation failed with {len(errors)} error(s)")
                for error in errors:
                    self._add_warning(state, f"Validation: {error}")
            
        except Exception as e:
            self._add_error(state, f"Validation failed: {str(e)}")
            state[self.output_field] = False
            state[self.errors_field] = [str(e)]
        
        return state


# ============================================================================
# CONDITIONAL ROUTER NODE
# ============================================================================

class ConditionalNode(BaseNode):
    """
    Node for conditional logic and routing decisions.
    
    This node evaluates conditions and sets routing flags.
    """
    
    def __init__(
        self,
        name: str,
        condition_func: Callable[[Dict[str, Any]], str],
        output_field: str = "next_step",
    ):
        """
        Initialize conditional node.
        
        Args:
            name: Node name
            condition_func: Function that returns the next step name
            output_field: State field to store routing decision
        """
        super().__init__(name, "conditional")
        self.condition_func = condition_func
        self.output_field = output_field
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate condition."""
        try:
            next_step = self.condition_func(state)
            state[self.output_field] = next_step
            self.logger.info(f"Routing to: {next_step}")
        except Exception as e:
            self._add_error(state, f"Condition evaluation failed: {str(e)}")
            state[self.output_field] = "error"
        
        return state


# ============================================================================
# DATA TRANSFORMATION NODE
# ============================================================================

class TransformNode(BaseNode):
    """
    Node for data transformation operations.
    
    This node applies transformations to data in the state.
    """
    
    def __init__(
        self,
        name: str,
        transform_func: Callable[[Any], Any],
        input_field: str,
        output_field: str,
    ):
        """
        Initialize transform node.
        
        Args:
            name: Node name
            transform_func: Function to transform the data
            input_field: State field to read input from
            output_field: State field to store output
        """
        super().__init__(name, "transform")
        self.transform_func = transform_func
        self.input_field = input_field
        self.output_field = output_field
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation."""
        try:
            input_data = state.get(self.input_field)
            
            if input_data is None:
                self._add_warning(state, f"No data in '{self.input_field}'")
                return state
            
            # Apply transformation
            output_data = self.transform_func(input_data)
            state[self.output_field] = output_data
            
            self.logger.info(f"Transformed data from '{self.input_field}' to '{self.output_field}'")
            
        except Exception as e:
            self._add_error(state, f"Transformation failed: {str(e)}")
        
        return state


# ============================================================================
# HELPER FUNCTIONS FOR NODE CREATION
# ============================================================================

def create_llm_node(
    name: str,
    prompt_template: str,
    system_prompt: Optional[str] = None,
    output_field: str = "llm_response",
    **kwargs
) -> LLMNode:
    """
    Convenient function to create an LLM node.
    
    Args:
        name: Node name
        prompt_template: Path to user prompt template
        system_prompt: Path to system prompt template or direct text
        output_field: Where to store the response
        **kwargs: Additional LLMNode parameters
        
    Returns:
        Configured LLMNode instance
    """
    return LLMNode(
        name=name,
        user_prompt_template=prompt_template,
        system_prompt_template=system_prompt,
        output_field=output_field,
        **kwargs
    )


def create_tool_node(
    name: str,
    tool_func: Callable,
    output_field: str = "tool_result",
    **kwargs
) -> ToolNode:
    """
    Convenient function to create a tool node.
    
    Args:
        name: Node name
        tool_func: Tool function to execute
        output_field: Where to store the result
        **kwargs: Additional ToolNode parameters
        
    Returns:
        Configured ToolNode instance
    """
    return ToolNode(
        name=name,
        tool_func=tool_func,
        output_field=output_field,
        **kwargs
    )


def create_validation_node(
    name: str,
    validation_func: Callable,
    output_field: str = "is_valid",
    **kwargs
) -> ValidationNode:
    """
    Convenient function to create a validation node.
    
    Args:
        name: Node name
        validation_func: Validation function
        output_field: Where to store validation result
        **kwargs: Additional ValidationNode parameters
        
    Returns:
        Configured ValidationNode instance
    """
    return ValidationNode(
        name=name,
        validation_func=validation_func,
        output_field=output_field,
        **kwargs
    )
