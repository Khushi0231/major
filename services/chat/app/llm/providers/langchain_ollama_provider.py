"""LangChain + Ollama Provider — Primary LLM engine for DRAVIS

Uses LangChain's ChatOllama integration for local, offline inference.
This is the preferred provider: free, private, no API keys needed.
"""
import logging
from typing import Dict, Any
import requests
from .base import LLMProvider

logger = logging.getLogger(__name__)


class LangChainOllamaProvider(LLMProvider):
    """Primary LLM provider using LangChain + Ollama for local inference."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.2:3b")
        self.timeout = config.get("timeout", 120)
        self.temperature = config.get("temperature", 0.7)
        self._llm = None

    def _get_llm(self):
        """Lazy-load the LangChain ChatOllama instance."""
        if self._llm is not None:
            return self._llm
        try:
            from langchain_ollama import ChatOllama
            self._llm = ChatOllama(
                base_url=self.base_url,
                model=self.model,
                temperature=self.temperature,
                num_predict=1000,
            )
            logger.info(f"LangChain+Ollama initialized: model={self.model}")
            return self._llm
        except ImportError:
            logger.error("langchain-ollama not installed. Run: pip install langchain-ollama")
            raise
        except Exception as e:
            logger.error(f"Failed to init LangChain+Ollama: {e}")
            raise

    def generate(self, prompt: str, **kwargs) -> str:
        llm = self._get_llm()

        # Override temperature/max_tokens per-call if provided
        temp = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", 1000)

        try:
            from langchain_core.messages import HumanMessage
            response = llm.invoke(
                [HumanMessage(content=prompt)],
                temperature=temp,
                num_predict=max_tokens,
            )
            return response.content
        except Exception as e:
            raise RuntimeError(f"LangChain+Ollama generation failed: {e}")

    def is_available(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "langchain_ollama",
            "model": self.model,
            "type": "local",
            "framework": "langchain",
            "base_url": self.base_url,
        }
