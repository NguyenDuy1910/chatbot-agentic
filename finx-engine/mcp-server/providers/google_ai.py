"""
Google AI (Gemini) LLM Provider
Handles integration with Google's Generative AI API
"""

import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from config import MCPServerConfig


logger = logging.getLogger(__name__)


class GoogleAIProvider:
    """Provider for Google AI (Gemini) LLM"""
    
    def __init__(self, config: MCPServerConfig):
        """Initialize Google AI provider"""
        self.config = config
        self.model_name = config.google_model
        self.timeout = config.google_timeout
        
        # Configure Google AI
        genai.configure(api_key=config.google_api_key)
        
        logger.info(f"Google AI provider initialized with model: {self.model_name}")
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        **kwargs
    ) -> str:
        """
        Generate text using Google AI
        
        Args:
            prompt: The input prompt
            temperature: Temperature for generation (0.0 - 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                **kwargs
            }
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**generation_config)
            )
            
            logger.debug(f"Generated text with {len(response.text)} characters")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    def generate_json(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_tokens: int = 8192,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON using Google AI
        
        Args:
            prompt: The input prompt
            schema: JSON schema for structured output
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            **kwargs: Additional generation parameters
            
        Returns:
            Generated JSON response as dictionary
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                **kwargs
            }
            
            # Add JSON schema if provided
            if schema:
                generation_config["response_mime_type"] = "application/json"
                generation_config["response_schema"] = schema
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**generation_config)
            )
            
            logger.debug(f"Generated JSON response")
            
            # Parse JSON response
            import json
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Error generating JSON: {e}")
            raise
    
    def analyze_text(
        self,
        text: str,
        analysis_type: str = "general",
        **kwargs
    ) -> str:
        """
        Analyze text using Google AI
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (general, sentiment, entities, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Analysis result
        """
        prompts = {
            "general": f"Analyze the following text:\n\n{text}",
            "sentiment": f"Perform sentiment analysis on:\n\n{text}",
            "entities": f"Extract named entities from:\n\n{text}",
            "summary": f"Summarize the following text:\n\n{text}",
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        return self.generate_text(prompt, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            model = genai.GenerativeModel(self.model_name)
            return {
                "model": self.model_name,
                "timeout": self.timeout,
                "provider": "google_ai"
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            raise

