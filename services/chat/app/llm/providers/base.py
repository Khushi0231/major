"""LLM Provider Base Class"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base for all LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a text response. Raises Exception on failure."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider is reachable and ready."""
        ...

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Return provider metadata for health/debug."""
        ...

    def __repr__(self) -> str:
        return f"<{self.name}>"
