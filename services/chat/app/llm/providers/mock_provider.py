"""Mock Provider - For testing without an actual LLM"""
import logging
from typing import Dict, Any
from .base import LLMProvider

logger = logging.getLogger(__name__)


class MockProvider(LLMProvider):
    """Returns canned responses — always available, zero latency."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        return (
            f"[MOCK] This is a test response for your query "
            f"(prompt length: {len(prompt)} chars, call #{self.call_count}). "
            f"Connect Ollama or set OPENAI_API_KEY for real responses."
        )

    def is_available(self) -> bool:
        return True

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "model": "mock-v1",
            "type": "testing",
            "call_count": self.call_count,
        }
