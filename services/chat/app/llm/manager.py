"""LLM Manager - Provider selection with automatic fallback

Priority order: Ollama (local) → OpenAI (cloud) → Mock (testing)
If Ollama is down, transparently falls through to the next available provider.
"""
import logging
from typing import Optional, Dict, Any, List
from .providers import LLMProvider, OllamaProvider, OpenAIProvider, GroqProvider, MockProvider

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages multiple LLM providers with priority-based fallback."""

    def __init__(self, config: Dict[str, Any]):
        self.providers: List[LLMProvider] = []
        self._init_providers(config)

    def _init_providers(self, config: Dict[str, Any]) -> None:
        # 1. Ollama (free, local, primary)
        ollama_cfg = config.get("ollama", {})
        try:
            self.providers.append(OllamaProvider(ollama_cfg))
            logger.info("Ollama provider registered")
        except Exception as e:
            logger.warning(f"Ollama init skipped: {e}")

        # 2. Groq (High-speed cloud, same models as Ollama, zero storage)
        groq_cfg = config.get("groq", {})
        if groq_cfg.get("api_key"):
            try:
                self.providers.append(GroqProvider(groq_cfg))
                logger.info("Groq provider registered")
            except Exception as e:
                logger.warning(f"Groq init skipped: {e}")

        # 3. OpenAI (cloud fallback)
        openai_cfg = config.get("openai", {})
        if openai_cfg.get("api_key"):
            try:
                self.providers.append(OpenAIProvider(openai_cfg))
                logger.info("OpenAI provider registered")
            except Exception as e:
                logger.warning(f"OpenAI init skipped: {e}")

        # 4. Mock (always-on safety net)
        self.providers.append(MockProvider({}))
        logger.info(f"LLM Manager ready with {len(self.providers)} provider(s)")

    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Try each provider in order until one succeeds."""
        errors: List[str] = []

        for provider in self.providers:
            try:
                if provider.is_available():
                    logger.info(f"Using provider: {provider.name}")
                    return provider.generate(prompt, **kwargs)
                else:
                    errors.append(f"{provider.name}: not available")
            except Exception as e:
                msg = f"{provider.name}: {e}"
                logger.warning(f"Provider failed — {msg}")
                errors.append(msg)

        logger.error(f"All providers failed: {'; '.join(errors)}")
        return None

    def get_active_provider(self) -> Optional[str]:
        """Return the name of the first available provider."""
        for p in self.providers:
            try:
                if p.is_available():
                    return p.name
            except Exception:
                continue
        return None

    def health(self) -> Dict[str, Any]:
        """Return availability status for every registered provider."""
        result = {}
        for p in self.providers:
            try:
                result[p.name] = {
                    "available": p.is_available(),
                    **p.get_info(),
                }
            except Exception as e:
                result[p.name] = {"available": False, "error": str(e)}
        return result
