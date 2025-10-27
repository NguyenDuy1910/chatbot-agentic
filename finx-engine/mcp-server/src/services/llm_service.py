"""
LLM Service for finx-ai-service.

Provides a unified interface for LLM operations across all graphs and pipelines.
Wraps the LLMProvider to offer high-level LLM functionality.
"""

import logging
from typing import Any, Dict, Optional

from src.core.provider import LLMProvider

logger = logging.getLogger(__name__)


class LLMService:
    """
    Unified LLM service for all graphs and pipelines.
    
    Provides a high-level interface for LLM operations including:
    - Text generation
    - Prompt building
    - Response parsing
    - Error handling
    """
    
    def __init__(self, provider: LLMProvider):
        """
        Initialize LLM service.
        
        Args:
            provider: LLMProvider instance for LLM operations
        """
        self.provider = provider
        logger.info(f"LLMService initialized with provider: {provider.__class__.__name__}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt for context
            temperature: Temperature for generation (0.0 - 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            logger.info(f"Generating text with prompt length: {len(prompt)}")
            
            generator = self.provider.get_generator(
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            result = await generator(prompt=prompt)
            
            # Extract response from result
            response = result.get("replies", [""])[0]
            logger.info(f"Generated response with length: {len(response)}")
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}", exc_info=True)
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured LLM model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.provider.get_model(),
            "model_kwargs": self.provider.get_model_kwargs(),
            "context_window_size": self.provider.get_context_window_size(),
        }
    
    def get_model(self) -> str:
        """
        Get the model name.
        
        Returns:
            Model name string
        """
        return self.provider.get_model()
    
    def get_context_window_size(self) -> int:
        """
        Get the context window size for the model.
        
        Returns:
            Context window size in tokens
        """
        return self.provider.get_context_window_size()


__all__ = [
    "LLMService",
]

