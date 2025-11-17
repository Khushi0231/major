import numpy as np
from backend.rag.rag_store import index, docs
from models.embedding_manager import embed_text

from backend.models.ollama_handler import OllamaHandler

# Use the SAME embedder used by chat
ollama = OllamaHandler()

def query_rag(query: str, top_k: int = 3):
    if len(docs) == 0:
        return []

    # Use ollama embedder
    query_emb = ollama.embedder.encode(query).astype("float32")

    D, I = index.search(np.array([query_emb]), top_k)

    results = []
    for idx in I[0]:
        if idx < len(docs):
            results.append(docs[idx])

    return results