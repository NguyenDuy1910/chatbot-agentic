import logging
from typing import Any, Dict, List, Optional, Union

from src.core.provider import LLMProvider
from src.core.providers import (
    GeminiProvider,
    LLMProviderFactory,
    OpenAIProvider,
    create_llm_provider,
)

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for LLM operations.
    
    Provides a unified interface for interacting with different LLM providers
    including Google Gemini and OpenAI GPT models.
    
    Features:
    - Multi-provider support (Gemini, OpenAI)
    - Async text generation
    - Batch generation
    - Structured output support
    - Conversation history management
    - Model information retrieval
    
    Example:
        >>> # Create service with Gemini
        >>> provider = create_llm_provider("gemini", model="gemini-2.0-flash-exp")
        >>> service = LLMService(provider)
        >>> response = await service.generate("What is Python?")
        
        >>> # Create service with OpenAI
        >>> provider = create_llm_provider("openai", model="gpt-4o-mini")
        >>> service = LLMService(provider)
        >>> response = await service.generate("Explain async/await")
    """
    
    def __init__(self, provider: LLMProvider):
        """
        Initialize LLM Service.
        
        Args:
            provider: LLMProvider instance (GeminiProvider, OpenAIProvider, etc.)
        """
        self.provider = provider
        self._current_model = provider.get_model()
        
        logger.info(
            f"LLMService initialized with {provider.__class__.__name__} "
            f"using model: {self._current_model}"
        )
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "LLMService":
        """
        Create LLMService from configuration dictionary.
        
        Args:
            config: Configuration with provider and model settings
            
        Returns:
            LLMService instance
            
        Example:
            >>> config = {
            ...     "provider": "gemini",
            ...     "model": "gemini-2.0-flash-exp",
            ...     "temperature": 0.7,
            ... }
            >>> service = LLMService.from_config(config)
        """
        provider = LLMProviderFactory.create_from_config(config)
        return cls(provider)
    
    @classmethod
    def create(
        cls,
        provider_type: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> "LLMService":
        """
        Create LLMService with specified provider and model.
        
        Args:
            provider_type: Provider type ('gemini', 'openai', etc.)
            model: Model name (auto-selected if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMService instance
            
        Example:
            >>> service = LLMService.create("gemini", model="gemini-2.0-flash-exp")
            >>> service = LLMService.create("openai", model="gpt-4o-mini", temperature=0.5)
        """
        provider = create_llm_provider(provider_type, model, **kwargs)
        return cls(provider)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt/question
            system_prompt: System instructions (optional)
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            response_format: Response format config for structured output
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
            
        Example:
            >>> response = await service.generate("What is Python?")
            >>> response = await service.generate(
            ...     "Explain classes",
            ...     system_prompt="You are a Python expert",
            ...     temperature=0.5
            ... )
        """
        try:
            logger.info(f"Generating text with model: {self._current_model}")
            
            # Build generation kwargs
            gen_kwargs = {}
            if temperature is not None:
                gen_kwargs["temperature"] = temperature
            if max_tokens is not None:
                gen_kwargs["max_tokens"] = max_tokens
            gen_kwargs.update(kwargs)
            
            # Check if provider has generate method
            if hasattr(self.provider, "generate"):
                response = await self.provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    response_format=response_format,
                    **gen_kwargs
                )
            else:
                # Fallback to callable interface
                result = await self.provider(
                    prompt,
                    system_prompt=system_prompt,
                    response_format=response_format,
                    **gen_kwargs
                )
                response = result.get("replies", [""])[0]
            
            logger.info("Text generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    async def generate_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        Generate text for multiple prompts in batch.
        
        Args:
            prompts: List of prompts
            system_prompt: System instructions (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated text responses
            
        Example:
            >>> prompts = ["What is Python?", "What is JavaScript?"]
            >>> responses = await service.generate_batch(prompts)
        """
        try:
            logger.info(f"Generating batch of {len(prompts)} prompts")
            
            if hasattr(self.provider, "generate_batch"):
                responses = await self.provider.generate_batch(
                    prompts=prompts,
                    system_prompt=system_prompt,
                    **kwargs
                )
            else:
                # Fallback: generate one by one
                import asyncio
                tasks = [
                    self.generate(prompt, system_prompt, **kwargs)
                    for prompt in prompts
                ]
                responses = await asyncio.gather(*tasks)
            
            logger.info(f"Batch generation completed: {len(responses)} responses")
            return responses
            
        except Exception as e:
            logger.error(f"Error in batch generation: {str(e)}")
            raise
    
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """
        Generate text with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Role can be 'system', 'user', or 'assistant'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
            
        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are a helpful assistant"},
            ...     {"role": "user", "content": "Hello"},
            ...     {"role": "assistant", "content": "Hi! How can I help?"},
            ...     {"role": "user", "content": "Tell me about Python"}
            ... ]
            >>> response = await service.generate_with_history(messages)
        """
        try:
            logger.info(f"Generating with conversation history ({len(messages)} messages)")
            
            if hasattr(self.provider, "generate_with_history"):
                response = await self.provider.generate_with_history(
                    messages=messages,
                    **kwargs
                )
            else:
                # Fallback: extract last user message and system prompt
                system_prompt = None
                user_prompt = ""
                
                for msg in messages:
                    if msg.get("role") == "system":
                        system_prompt = msg.get("content", "")
                    elif msg.get("role") == "user":
                        user_prompt = msg.get("content", "")
                
                response = await self.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
            
            logger.info("Generated text with history successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error generating with history: {str(e)}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate JSON output using structured output.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions (optional)
            **kwargs: Additional generation parameters
            
        Returns:
            Parsed JSON response as dictionary
            
        Example:
            >>> response = await service.generate_json(
            ...     "List 3 fruits in JSON format",
            ...     system_prompt="Return only valid JSON"
            ... )
        """
        try:
            import json
            
            logger.info("Generating JSON output")
            
            # Set response format to JSON
            response_format = {"type": "json_object"}
            
            response_text = await self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format,
                **kwargs
            )
            
            # Parse JSON
            response_json = json.loads(response_text)
            
            logger.info("JSON output generated and parsed successfully")
            return response_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Error generating JSON: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information including:
            - model: Model name
            - provider: Provider class name
            - context_window: Context window size in tokens
            - parameters: Model configuration parameters
            
        Example:
            >>> info = service.get_model_info()
            >>> print(f"Model: {info['model']}")
            >>> print(f"Context window: {info['context_window']} tokens")
        """
        try:
            info = {
                "model": self.provider.get_model(),
                "provider": self.provider.__class__.__name__,
                "context_window": self.provider.get_context_window_size(),
                "parameters": self.provider.get_model_kwargs(),
            }
            
            logger.info(f"Retrieved model info: {info['model']}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            raise
    
    def get_provider(self) -> LLMProvider:
        """
        Get the underlying LLM provider.
        
        Returns:
            LLMProvider instance
        """
        return self.provider
    
    def get_context_window_size(self) -> int:
        """
        Get context window size in tokens.
        
        Returns:
            Context window size
        """
        return self.provider.get_context_window_size()
    
    @property
    def model_name(self) -> str:
        """Get current model name."""
        return self._current_model
    
    @property
    def provider_name(self) -> str:
        """Get provider class name."""
        return self.provider.__class__.__name__

