"""
backend/models/llm_loader.py

Adapter so main.py can import `generate` as expected.

It creates a single OllamaHandler() instance and exposes a `generate(...)` function
that accepts flexible arguments (so older callers that pass `language=...` don't break).
"""

import logging
from typing import Optional

logger = logging.getLogger("llm_loader")

try:
    # Use relative import for module inside backend/models
    from .ollama_handler import OllamaHandler
except Exception as e:
    logger.exception("Failed to import OllamaHandler: %s", e)
    # Fallback stub
    class OllamaHandler:
        def __init__(self): pass
        def is_available(self): return False
        def generate(self, prompt, **kwargs): return None
        def embed(self, text): return []

# Singleton handler
_handler = OllamaHandler()

def generate(prompt: str, max_tokens: int = 512, temperature: float = 0.0, **kwargs) -> Optional[str]:
    """
    Wrapper used by main.py.

    Accepts flexible kwargs so that callers which pass language / mode won't crash.
    Returns generated text string, or None on failure.
    """
    try:
        if not hasattr(_handler, "generate") or not _handler.is_available():
            logger.debug("LLM handler not available.")
            return None
        return _handler.generate(prompt=prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
    except Exception as e:
        logger.exception("llm_loader.generate exception: %s", e)
        return None