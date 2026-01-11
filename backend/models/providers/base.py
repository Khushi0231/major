"""Base LLM Provider Interface

This module defines the abstract base class for all LLM providers.
All provider implementations must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self.name = self.__class__.__name__
        logger.info(f"Initializing {self.name}")

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response from the LLM.
        
        Args:
            prompt: Input text prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available and ready to use.
        
        Returns:
            True if provider is available, False otherwise
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.
        
        Returns:
            Dictionary containing model information
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the provider.
        
        Returns:
            Dictionary with health status information
        """
        try:
            is_available = await self.is_available()
            return {
                "provider": self.name,
                "status": "healthy" if is_available else "unhealthy",
                "available": is_available,
                "model_info": self.get_model_info() if is_available else None
            }
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return {
                "provider": self.name,
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def __repr__(self) -> str:
        return f"<{self.name} provider>"
