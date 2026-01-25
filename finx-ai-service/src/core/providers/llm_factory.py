import logging
from typing import Any, Dict, Optional

from src.core.provider import LLMProvider
from src.core.providers.gemini_provider import GeminiProvider
from src.core.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory for creating LLM providers.
    
    Supports:
    - Gemini (Google Generative AI)
    - OpenAI (GPT models)
    """
    
    # Registry of available providers
    _providers = {
        "gemini": GeminiProvider,
        "google_genai": GeminiProvider,
        "openai": OpenAIProvider,
        "gpt": OpenAIProvider,
    }
    
    @classmethod
    def create_provider(
        cls,
        provider_type: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_type: Type of provider ('gemini', 'openai', etc.)
            model: Model name (auto-selected if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_type_lower = provider_type.lower()
        
        if provider_type_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported provider type: {provider_type}. "
                f"Available providers: {available}"
            )
        
        provider_class = cls._providers[provider_type_lower]
        
        # Create provider with model and kwargs
        if model:
            kwargs["model"] = model
        
        logger.info(f"Creating {provider_type} provider with model: {model}")
        
        try:
            provider = provider_class(**kwargs)
            logger.info(f"Successfully created {provider_type} provider")
            return provider
        except Exception as e:
            logger.error(f"Failed to create {provider_type} provider: {e}")
            raise
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> LLMProvider:
        """
        Create provider from configuration dictionary.
        
        Args:
            config: Configuration dict with keys:
                - provider: Provider type
                - model: Model name
                - temperature: Temperature (optional)
                - max_tokens/max_output_tokens: Max tokens (optional)
                - Other model-specific parameters
            
        Returns:
            LLMProvider instance
        """
        provider_type = config.get("provider")
        if not provider_type:
            raise ValueError("Configuration must include 'provider' key")
        
        model = config.get("model")
        
        # Extract common parameters
        kwargs = {}
        
        if "temperature" in config:
            kwargs["temperature"] = config["temperature"]
        
        if "max_tokens" in config:
            kwargs["max_tokens"] = config["max_tokens"]
        elif "max_output_tokens" in config:
            kwargs["max_output_tokens"] = config["max_output_tokens"]
        
        if "top_p" in config:
            kwargs["top_p"] = config["top_p"]
        
        if "top_k" in config:
            kwargs["top_k"] = config["top_k"]
        
        if "api_key" in config:
            kwargs["api_key"] = config["api_key"]
        
        # Add any additional kwargs
        for key, value in config.items():
            if key not in ["provider", "model"] and key not in kwargs:
                kwargs[key] = value
        
        return cls.create_provider(provider_type, model, **kwargs)
    
    @classmethod
    def register_provider(
        cls,
        provider_type: str,
        provider_class: type,
    ):
        """
        Register a custom provider class.
        
        Args:
            provider_type: Identifier for the provider
            provider_class: Provider class (must inherit from LLMProvider)
        """
        if not issubclass(provider_class, LLMProvider):
            raise TypeError(
                f"Provider class must inherit from LLMProvider, "
                f"got {provider_class}"
            )
        
        cls._providers[provider_type.lower()] = provider_class
        logger.info(f"Registered custom provider: {provider_type}")
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of available provider types.
        
        Returns:
            List of provider type names
        """
        return list(cls._providers.keys())


# Convenience function
def create_llm_provider(
    provider_type: str,
    model: Optional[str] = None,
    **kwargs: Any,
) -> LLMProvider:
    """
    Convenience function to create an LLM provider.
    
    Args:
        provider_type: Type of provider ('gemini', 'openai', etc.)
        model: Model name (auto-selected if None)
        **kwargs: Additional provider-specific parameters
        
    Returns:
        LLMProvider instance
    """
    return LLMProviderFactory.create_provider(provider_type, model, **kwargs)
