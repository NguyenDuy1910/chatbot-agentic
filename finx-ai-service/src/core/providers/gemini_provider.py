import asyncio
import logging
import os
from typing import Any, Dict, Optional

from src.core.provider import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Google Gemini LLM Provider.
    
    Supports Google's Gemini models including:
    - gemini-2.0-flash-exp
    - gemini-1.5-pro
    - gemini-1.5-flash
    """
    
    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        top_p: float = 0.95,
        top_k: int = 40,
        **kwargs: Any,
    ):
        """
        Initialize Gemini Provider.
        
        Args:
            model: Model name (e.g., 'gemini-2.0-flash-exp')
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            temperature: Sampling temperature (0.0 to 1.0)
            max_output_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            **kwargs: Additional model parameters
        """
        self._model = model
        self._api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._top_p = top_p
        self._top_k = top_k
        self._model_kwargs = kwargs
        
        # Set context window size based on model
        if "flash" in model.lower():
            self._context_window_size = 1048576  # 1M tokens for flash models
        elif "pro" in model.lower():
            self._context_window_size = 2097152  # 2M tokens for pro models
        else:
            self._context_window_size = 32768  # Default
        
        self._client = None
        self._initialize_client()
        
        logger.info(f"GeminiProvider initialized with model: {model}")
    
    def _initialize_client(self):
        """Initialize Google Generative AI client."""
        try:
            import google.generativeai as genai
            
            if not self._api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(self._model)
            
            logger.info("Google Generative AI client initialized successfully")
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
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
        Generate text using Gemini model.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions (optional)
            response_format: Response format configuration (for structured output)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            # Combine prompts
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Build generation config
            generation_config = {
                "temperature": kwargs.get("temperature", self._temperature),
                "max_output_tokens": kwargs.get("max_output_tokens", self._max_output_tokens),
                "top_p": kwargs.get("top_p", self._top_p),
                "top_k": kwargs.get("top_k", self._top_k),
            }
            
            # Add JSON mode if response format specified
            if response_format:
                generation_config["response_mime_type"] = "application/json"
            
            # Merge with override kwargs
            if hasattr(self, "_override_kwargs"):
                generation_config.update(self._override_kwargs)
            
            # Generate content (async wrapper for sync API)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
            )
            
            logger.info("Generated text successfully with Gemini")
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
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
        return {
            "temperature": self._temperature,
            "max_output_tokens": self._max_output_tokens,
            "top_p": self._top_p,
            "top_k": self._top_k,
            **self._model_kwargs,
        }
    
    def get_context_window_size(self) -> int:
        """Get context window size in tokens."""
        return self._context_window_size
