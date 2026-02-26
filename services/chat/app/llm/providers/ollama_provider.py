"""Ollama Raw API Provider — Secondary/Mistral fallback for DRAVIS"""
import logging
from typing import Dict, Any
import requests
from .base import LLMProvider
from .langchain_ollama_provider import SYSTEM_PROMPT  # Reuse same system prompt

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Raw Ollama REST API — used as fallback when LangChain+Ollama fails."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "mistral")
        self.timeout = config.get("timeout", 120)

    def generate(self, prompt: str, **kwargs) -> str:
        # Prepend system prompt as text since raw /api/generate uses single prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}\n\nAssistant:"
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.6),
                        "num_predict": kwargs.get("max_tokens", 2048),
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                    },
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            text = resp.json().get("response", "").strip()
            if not text:
                raise ValueError("Empty response from Ollama")
            return text
        except requests.ConnectionError:
            raise ConnectionError(f"Cannot reach Ollama at {self.base_url}. Is Ollama running?")
        except requests.Timeout:
            raise TimeoutError(f"Ollama timed out after {self.timeout}s")
        except KeyError:
            raise ValueError("Invalid response format from Ollama")

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            model_base = self.model.split(":")[0]
            return any(model_base in m for m in models)
        except Exception:
            return False

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "ollama_raw",
            "model": self.model,
            "type": "local",
            "base_url": self.base_url,
        }
