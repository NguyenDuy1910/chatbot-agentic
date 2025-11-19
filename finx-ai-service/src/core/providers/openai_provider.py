"""
OpenAI LLM Provider Implementation.

Provides integration with OpenAI's GPT models.
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from src.core.provider import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM Provider.
    
    Supports OpenAI models including:
    - gpt-4o
    - gpt-4o-mini
    - gpt-4-turbo
    - gpt-3.5-turbo
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        **kwargs: Any,
    ):
        """
        Initialize OpenAI Provider.
        
        Args:
            model: Model name (e.g., 'gpt-4o-mini')
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            **kwargs: Additional model parameters
        """
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._top_p = top_p
        self._frequency_penalty = frequency_penalty
        self._presence_penalty = presence_penalty
        self._model_kwargs = kwargs
        
        # Set context window size based on model
        if "gpt-4o" in model.lower():
            self._context_window_size = 128000  # 128k tokens
        elif "gpt-4-turbo" in model.lower():
            self._context_window_size = 128000  # 128k tokens
        elif "gpt-4" in model.lower():
            self._context_window_size = 8192  # 8k tokens
        elif "gpt-3.5-turbo" in model.lower():
            self._context_window_size = 16385  # 16k tokens
        else:
            self._context_window_size = 4096  # Default
        
        self._client = None
        self._initialize_client()
        
        logger.info(f"OpenAIProvider initialized with model: {model}")
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI
            
            if not self._api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self._client = AsyncOpenAI(api_key=self._api_key)
            
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def get_generator(self, **override_kwargs: Any):
        """
        Get generator instance for text generation.
        
        Args:
            **override_kwargs: Override default model parameters
            
        Returns:
            Self (for async generation)
        """
        # Store override kwargs for generation
        self._override_kwargs = override_kwargs
        return self
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using OpenAI model.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions (optional)
            response_format: Response format configuration (for structured output)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Build parameters
            params = {
                "model": self._model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self._temperature),
                "top_p": kwargs.get("top_p", self._top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self._frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self._presence_penalty),
            }
            
            # Add max_tokens if specified
            if self._max_tokens or "max_tokens" in kwargs:
                params["max_tokens"] = kwargs.get("max_tokens", self._max_tokens)
            
            # Add response format if specified
            if response_format:
                params["response_format"] = response_format
            
            # Merge with override kwargs
            if hasattr(self, "_override_kwargs"):
                params.update(self._override_kwargs)
            
            # Generate completion
            response = await self._client.chat.completions.create(**params)
            
            logger.info("Generated text successfully with OpenAI")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def generate_batch(
        self,
        prompts: list[str],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> list[str]:
        """
        Generate text for multiple prompts in batch.
        
        Args:
            prompts: List of prompts
            system_prompt: System instructions (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated texts
        """
        tasks = [
            self.generate(prompt, system_prompt, **kwargs)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)
    
    async def generate_with_history(
        self,
        messages: list[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """
        Generate text with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            params = {
                "model": self._model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self._temperature),
                "top_p": kwargs.get("top_p", self._top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self._frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self._presence_penalty),
            }
            
            if self._max_tokens or "max_tokens" in kwargs:
                params["max_tokens"] = kwargs.get("max_tokens", self._max_tokens)
            
            if hasattr(self, "_override_kwargs"):
                params.update(self._override_kwargs)
            
            response = await self._client.chat.completions.create(**params)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation with history error: {e}")
            raise
    
    async def __call__(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Make provider callable (for compatibility).
        
        Args:
            prompt: User prompt
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with 'replies' key containing generated text
        """
        system_prompt = kwargs.pop("system_prompt", None)
        response_format = kwargs.pop("response_format", None)
        
        result = await self.generate(prompt, system_prompt, response_format, **kwargs)
        
        return {"replies": [result]}
    
    def get_model(self) -> str:
        """Get model name."""
        return self._model
    
    def get_model_kwargs(self) -> Dict[str, Any]:
        """Get model configuration parameters."""
        params = {
            "temperature": self._temperature,
            "top_p": self._top_p,
            "frequency_penalty": self._frequency_penalty,
            "presence_penalty": self._presence_penalty,
        }
        
        if self._max_tokens:
            params["max_tokens"] = self._max_tokens
        
        params.update(self._model_kwargs)
        return params
    
    def get_context_window_size(self) -> int:
        """Get context window size in tokens."""
        return self._context_window_size
