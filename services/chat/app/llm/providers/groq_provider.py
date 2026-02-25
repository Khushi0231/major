"""Groq Provider - High-speed Cloud LLM (same models as Ollama)"""
import logging
from typing import Dict, Any
import requests
from .base import LLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """
    Connects to Groq API. 
    Provides SAME models as Ollama (Llama, Mistral) with zero local storage.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        # Standard models that match Ollama offerings
        self.model = config.get("model", "llama-3.1-8b-instant")
        self.base_url = "https://api.groq.com/openai/v1"

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.api_key:
            raise ValueError("Groq API key not provided")
        
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 1000),
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Groq generation failed: {e}")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "groq",
            "model": self.model,
            "type": "cloud",
            "speed": "extremely-fast",
            "requires_api_key": True
        }
