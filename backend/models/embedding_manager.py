"""Manages text embeddings using sentence-transformers"""
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

_embedder = None


def get_embedder():
    """Get or initialize sentence-transformers embedder"""
    global _embedder
    
    if _embedder is not None:
        return _embedder
    
    try:
        from sentence_transformers import SentenceTransformer
        # Use a lightweight model for offline use
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
        return _embedder
    except Exception as e:
        logger.error(f"Failed to load sentence-transformers: {e}")
        return None


class EmbeddingManager:
    def __init__(self):
        self.embedder = get_embedder()
        self.cache = {}
    
    def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not text or not text.strip():
            return None
        
        # Check cache
        text_key = text[:100]  # Cache key (first 100 chars)
        if text_key in self.cache:
            return self.cache[text_key]
        
        if self.embedder is None:
            logger.error("Embedder not available")
            return None
        
        try:
            embedding = self.embedder.encode(text, convert_to_numpy=True).tolist()
            self.cache[text_key] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        if not self.embedder:
            return [None] * len(texts)
        
        try:
            embeddings = self.embedder.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [None] * len(texts)
    
    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not emb1 or not emb2:
            return 0.0
        
        try:
            a, b = np.array(emb1), np.array(emb2)
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
