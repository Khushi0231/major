"""Ollama Provider - Refactored for local LLM"""
import requests
from typing import Dict, Any
from .base import LLMProvider
import logging

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.1:8b")
        self.timeout = config.get("timeout", 30)
        logger.info(f"OllamaProvider initialized for {self.base_url}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 1000)
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timed out after {self.timeout}s")
        except KeyError:
            raise Exception("Invalid response format from Ollama")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"Ollama error: {str(e)}")
    
    async def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return Ollama model info"""
        return {
            "provider": "ollama",
            "model": self.model,
            "type": "local",
            "base_url": self.base_url,
            "timeout": self.timeout
        }
