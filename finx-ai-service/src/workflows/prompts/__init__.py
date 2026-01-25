"""
Workflow Prompts Package

This package contains all prompt templates for workflows and the PromptManager
for loading and rendering them.

Usage:
    from src.workflows.prompts import render_prompt
    
    prompt = render_prompt(
        "intent_recommendation/classification_system.jinja2",
        context={"db_schemas": schemas}
    )
"""

from .prompt_manager import (
    PromptManager,
    get_prompt_manager,
    render_prompt,
)

__all__ = [
    "PromptManager",
    "get_prompt_manager",
    "render_prompt",
]

