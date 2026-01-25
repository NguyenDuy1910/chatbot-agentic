"""
Prompt Manager

This module provides a centralized way to load and render Jinja2 prompt templates.
All prompts are stored as .jinja2 files in the prompts/ directory.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import logging

logger = logging.getLogger("finx-ai-service.workflows.prompts")


class PromptManager:
    """
    Manages loading and rendering of Jinja2 prompt templates.
    
    Usage:
        manager = PromptManager()
        prompt = manager.render(
            "intent_recommendation/classification_system.jinja2",
            context={"db_schemas": schemas}
        )
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize the PromptManager.
        
        Args:
            prompts_dir: Path to the prompts directory. If None, uses default location.
        """
        if prompts_dir is None:
            # Default to src/workflows/prompts
            current_file = Path(__file__)
            prompts_dir = current_file.parent
        
        self.prompts_dir = Path(prompts_dir)
        
        if not self.prompts_dir.exists():
            raise ValueError(f"Prompts directory does not exist: {self.prompts_dir}")
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        
        logger.info(f"PromptManager initialized with directory: {self.prompts_dir}")
    
    def render(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a prompt template with the given context.
        
        Args:
            template_name: Name of the template file (e.g., "intent_recommendation/classification_system.jinja2")
            context: Dictionary of variables to pass to the template
        
        Returns:
            Rendered prompt string
        
        Raises:
            TemplateNotFound: If the template file doesn't exist
        """
        if context is None:
            context = {}
        
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**context)
            logger.debug(f"Rendered template: {template_name}")
            return rendered
        except TemplateNotFound:
            logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise
    
    def get_template(self, template_name: str) -> Template:
        """
        Get a Jinja2 Template object for advanced usage.
        
        Args:
            template_name: Name of the template file
        
        Returns:
            Jinja2 Template object
        """
        return self.env.get_template(template_name)
    
    def list_templates(self, pattern: str = "*.jinja2") -> list[str]:
        """
        List all available templates matching the pattern.
        
        Args:
            pattern: Glob pattern to match (default: "*.jinja2")
        
        Returns:
            List of template paths relative to prompts_dir
        """
        templates = []
        for path in self.prompts_dir.rglob(pattern):
            relative_path = path.relative_to(self.prompts_dir)
            templates.append(str(relative_path))
        return sorted(templates)
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            template_name: Name of the template file
        
        Returns:
            True if template exists, False otherwise
        """
        template_path = self.prompts_dir / template_name
        return template_path.exists()


# Global singleton instance
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get the global PromptManager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


def render_prompt(template_name: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function to render a prompt using the global PromptManager.
    
    Args:
        template_name: Name of the template file
        context: Dictionary of variables to pass to the template
    
    Returns:
        Rendered prompt string
    """
    manager = get_prompt_manager()
    return manager.render(template_name, context)


__all__ = [
    "PromptManager",
    "get_prompt_manager",
    "render_prompt",
]

