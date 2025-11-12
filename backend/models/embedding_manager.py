
"""Manages text embeddings using Ollama"""
import numpy as np
from typing import List
from .ollama_handler import OllamaHandler

class EmbeddingManager:
    def __init__(self, ollama: OllamaHandler = None):
        self.ollama = ollama or OllamaHandler()
        self.cache = {}
    
    def embed(self, text: str) -> List[float]:
        if text in self.cache:
            return self.cache[text]
        embedding = self.ollama.embed(text)
        self.cache[text] = embedding
        return embedding
    
    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        if not emb1 or not emb2:
            return 0.0
        a, b = np.array(emb1), np.array(emb2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
