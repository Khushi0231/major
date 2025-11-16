"""
backend/models/ollama_handler.py

Provides:
 - OllamaHandler class with .generate(prompt, ...) and .embed(text) methods.
 - Uses llama_cpp (if installed and a GGUF model file exists) for generation.
 - Uses sentence-transformers (if installed) for embeddings as a fallback.
 - Safe, defensive: when models/packages are missing it logs and returns None/empty.
"""

import os
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama_handler")

# Path to a GGUF / llama.cpp-compatible file in the same folder as this file
DEFAULT_MODEL_FILENAME = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH = os.path.join(os.path.dirname(__file__), DEFAULT_MODEL_FILENAME)

# Globals
_llm = None
_embedding_model = None

# ------------------------------
# Try initializing llama_cpp LLM
# ------------------------------
try:
    from llama_cpp import Llama  # type: ignore

    if os.path.exists(MODEL_PATH):
        try:
            _llm = Llama(model_path=MODEL_PATH, n_ctx=4096)
            logger.info("Loaded local GGUF model at %s", MODEL_PATH)
        except Exception as e:
            logger.exception("Failed to init Llama model: %s", e)
            _llm = None
    else:
        logger.warning("Model file not found at %s. LLM unavailable.", MODEL_PATH)
except Exception as e:
    logger.warning("llama_cpp not available: %s", e)
    _llm = None


# ----------------------------------------
# Try initializing SentenceTransformer model
# ----------------------------------------
try:
    from sentence_transformers import SentenceTransformer  # type: ignore

    try:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Loaded embedding model (all-MiniLM-L6-v2)")
    except Exception as e:
        logger.exception("Failed to load SentenceTransformer: %s", e)
        _embedding_model = None
except Exception as e:
    logger.info("sentence-transformers not available: %s", e)
    _embedding_model = None


# ============================================================
#                     OLLAMA HANDLER CLASS
# ============================================================
class OllamaHandler:
    """
    Wrapper for:
     - llama.cpp generation
     - sentence-transformers embeddings
    """

    def __init__(self):
        self._llm = _llm
        self._embed = _embedding_model

    def is_available(self) -> bool:
        return self._llm is not None

    # ------------------------------------------------------------
    # FIXED generate() — adds the correct Mistral-Instruct template
    # ------------------------------------------------------------
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.0,
        **kwargs
    ) -> Optional[str]:

        if self._llm is None:
            logger.debug("generate() called but LLM is not available.")
            return None

        try:
            # Apply Mistral-Instruct template
            formatted_prompt = f"[INST] {prompt.strip()} [/INST]"

            res = self._llm(
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # ------------------------
            # Parse llama.cpp response
            # ------------------------
            if isinstance(res, dict):
                choices = res.get("choices", [])
                if choices and isinstance(choices, list):
                    text = choices[0].get("text", "")
                else:
                    text = res.get("text", "") or ""
            else:
                text = str(res)

            return (text or "").strip()

        except Exception as e:
            logger.exception("LLM generate failed: %s", e)
            return None

    # ------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------
    def embed(self, text: str) -> List[float]:
        if self._embed is None:
            logger.debug("embed() called but no embedding model available.")
            return []

        try:
            vector = self._embed.encode(text)
            return vector.tolist() if hasattr(vector, "tolist") else list(vector)
        except Exception as e:
            logger.exception("Embedding failed: %s", e)
            return []
