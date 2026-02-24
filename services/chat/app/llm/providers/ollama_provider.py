"""Ollama Provider - Local LLM via Ollama REST API"""
import logging
from typing import Dict, Any
import requests
from .base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Connects to a running Ollama instance for local inference."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.1:8b")
        self.timeout = config.get("timeout", 120)

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "num_predict": kwargs.get("max_tokens", 1000),
                    },
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot reach Ollama at {self.base_url}. Is Ollama running?"
            )
        except requests.Timeout:
            raise TimeoutError(
                f"Ollama timed out after {self.timeout}s"
            )
        except KeyError:
            raise ValueError("Invalid response format from Ollama")

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "ollama",
            "model": self.model,
            "type": "local",
            "base_url": self.base_url,
        }
