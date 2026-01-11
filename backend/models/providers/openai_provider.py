"""OpenAI Provider for Cloud LLM"""
import os
from typing import Dict, Any
from .base import LLMProvider
import logging

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider for cloud deployment"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.7)
        self.client = None
        
        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
            except Exception as e:
                logger.error(f"Error initializing OpenAI: {e}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Check API key and installation.")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available"""
        if not self.api_key or not self.client:
            return False
        
        try:
            # Simple API test
            self.client.models.list()
            return True
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return OpenAI model info"""
        return {
            "provider": "openai",
            "model": self.model,
            "type": "cloud",
            "temperature": self.temperature,
            "api_key_set": bool(self.api_key)
        }
