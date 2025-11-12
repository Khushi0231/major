
"""Retrieval-Augmented Generation pipeline"""
from typing import List, Dict, Tuple
from ..models.embedding_manager import EmbeddingManager

class Retriever:
    def __init__(self, embedding_manager: EmbeddingManager = None):
        self.em = embedding_manager or EmbeddingManager()
        self.documents = []
        self.embeddings = []
    
    def add_document(self, doc_id: str, text: str) -> None:
        self.documents.append({"id": doc_id, "text": text})
        self.embeddings.append(self.em.embed(text))
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.documents:
            return []
        query_emb = self.em.embed(query)
        scores = [self.em.similarity(query_emb, emb) for emb in self.embeddings]
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.documents[i] for i in top_indices]
