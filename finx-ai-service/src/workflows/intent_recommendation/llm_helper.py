"""
LLM Helper for Intent Recommendation Demo.

Provides simple LLM generation using Google Gemini or OpenAI.
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("finx-ai-service")


class SimpleLLMGenerator:
    """
    Simple LLM generator wrapper for demo purposes.
    
    Supports:
    - Google Gemini (via google-generativeai)
    - OpenAI (via openai)
    """
    
    def __init__(
        self,
        provider: str = "gemini",
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        Initialize LLM generator.
        
        Args:
            provider: "gemini" or "openai"
            model: Model name (auto-select if None)
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
        """
        self.provider = provider.lower()
        self.temperature = temperature
        self.kwargs = kwargs
        
        if self.provider == "gemini":
            self.model = model or "gemini-2.0-flash-exp"
            self._init_gemini()
        elif self.provider == "openai":
            self.model = model or "gpt-4o-mini"
            self._init_openai()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.info(f"SimpleLLMGenerator initialized with {self.provider}/{self.model}")
    
    def _init_gemini(self):
        """Initialize Google Gemini."""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
            logger.info("Google Gemini initialized")
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
    
    def _clean_schema_for_gemini(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean Pydantic JSON schema for Gemini compatibility.
        
        Gemini doesn't support certain fields like: title, $defs, allOf, anyOf, etc.
        """
        cleaned = {}
        
        # Fields to skip
        skip_fields = {"title", "$defs", "definitions", "allOf", "anyOf", "oneOf", "additionalProperties"}
        
        for key, value in schema.items():
            if key in skip_fields:
                continue
            
            if isinstance(value, dict):
                cleaned[key] = self._clean_schema_for_gemini(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._clean_schema_for_gemini(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                cleaned[key] = value
        
        return cleaned
    
    def _init_openai(self):
        """Initialize OpenAI."""
        try:
            from openai import AsyncOpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI initialized")
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate text using LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            response_format: Response format configuration (for structured output)
            
        Returns:
            Generated text
        """
        try:
            if self.provider == "gemini":
                return await self._generate_gemini(prompt, system_prompt, response_format)
            elif self.provider == "openai":
                return await self._generate_openai(prompt, system_prompt, response_format)
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate using Google Gemini."""
        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Configure generation
            generation_config = {
                "temperature": self.temperature,
            }
            
            # If response format is provided, just use JSON mode (not strict schema)
            if response_format:
                generation_config["response_mime_type"] = "application/json"
            
            # Generate (using sync method wrapped in async)
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(full_prompt, generation_config=generation_config)
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate using OpenAI."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            # Prepare kwargs
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
            }
            
            # Add response format if provided
            if response_format:
                kwargs["response_format"] = response_format
            
            # Generate
            response = await self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def __call__(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Make generator callable (compatible with existing code).
        
        Args:
            prompt: User prompt
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with 'replies' key containing generated text
        """
        system_prompt = kwargs.get("system_prompt")
        response_format = kwargs.get("response_format")
        
        result = await self.generate(prompt, system_prompt, response_format)
        
        return {"replies": [result]}


def create_llm_generator(
    provider: str = "gemini",
    model: Optional[str] = None,
    temperature: float = 0.7,
) -> SimpleLLMGenerator:
    """
    Factory function to create LLM generator.
    
    Args:
        provider: "gemini" or "openai"
        model: Model name (auto-select if None)
        temperature: Sampling temperature
        
    Returns:
        SimpleLLMGenerator instance
    """
    return SimpleLLMGenerator(provider=provider, model=model, temperature=temperature)
