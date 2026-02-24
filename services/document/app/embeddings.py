"""Document Service - Embedding Manager (sentence-transformers)"""
import logging
from typing import List, Optional
from .config import settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
        return _model
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return None


def embed_text(text: str) -> Optional[List[float]]:
    """Embed a single text string."""
    model = _get_model()
    if model is None or not text.strip():
        return None
    try:
        return model.encode(text, convert_to_numpy=True).tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return None


def embed_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """Embed a batch of texts."""
    model = _get_model()
    if model is None:
        return [None] * len(texts)
    try:
        embeddings = model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        return [None] * len(texts)


def is_ready() -> bool:
    return _get_model() is not None
