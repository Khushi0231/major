"""Mock LLM Provider for Testing"""
from typing import Dict, Any
from .base import LLMProvider
import logging

logger = logging.getLogger(__name__)

class MockProvider(LLMProvider):
    """Mock provider for testing without actual LLM"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.responses = config.get("mock_responses", [
            "This is a mock response from the test LLM.",
            "Mock LLM is working correctly!",
            "Testing response generation..."
        ])
        self.call_count = 0
        logger.info("MockProvider initialized")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response"""
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return f"[MOCK] {response} (prompt length: {len(prompt)} chars)"
    
    async def is_available(self) -> bool:
        """Mock is always available"""
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return mock model info"""
        return {
            "provider": "mock",
            "model": "mock-llm-v1",
            "type": "testing",
            "call_count": self.call_count
        }
