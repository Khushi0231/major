
"""ChromaDB vector store wrapper"""
from typing import List, Dict

class ChromaStore:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.docs = {}
        self.vectors = {}
    
    def add(self, doc_id: str, text: str, embedding: List[float]):
        self.docs[doc_id] = text
        self.vectors[doc_id] = embedding
    
    def query(self, embedding: List[float], top_k: int = 3) -> List[Dict]:
        if not self.vectors:
            return []
        import numpy as np
        query_vec = np.array(embedding)
        scores = {}
        for doc_id, vec in self.vectors.items():
            vec_arr = np.array(vec)
            score = np.dot(query_vec, vec_arr) / (np.linalg.norm(query_vec) * np.linalg.norm(vec_arr) + 1e-8)
            scores[doc_id] = score
        top_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
        return [{"id": doc_id, "text": self.docs[doc_id], "score": scores[doc_id]} for doc_id in top_ids]
