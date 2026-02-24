"""OpenAI Provider - Cloud LLM fallback"""
import logging
from typing import Dict, Any
from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI ChatCompletion API — used as fallback when Ollama is unavailable."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.7)
        self.client = None

        if self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.error("openai package not installed")
            except Exception as e:
                logger.error(f"OpenAI init failed: {e}")

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 1000),
            )
            return resp.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")

    def is_available(self) -> bool:
        if not self.api_key or not self.client:
            return False
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model,
            "type": "cloud",
            "api_key_set": bool(self.api_key),
        }
