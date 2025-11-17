from models.embedding_manager import embed_text

import faiss
import numpy as np
import os
import pickle

# Store location
FAISS_INDEX_PATH = "backend/rag/faiss.index"
DOC_STORE_PATH = "backend/rag/docs.pkl"

# Global objects
embedding_dim = 384  # MiniLM-L6-v2 output size
index = None
docs = []

def load_store():
    global index, docs
    
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(embedding_dim)

    if os.path.exists(DOC_STORE_PATH):
        with open(DOC_STORE_PATH, "rb") as f:
            docs.extend(pickle.load(f))

load_store()


def save_store():
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(DOC_STORE_PATH, "wb") as f:
        pickle.dump(docs, f)


def add_document(text: str, embedding: np.ndarray):
    global index, docs
    
    embedding = embedding.astype("float32")  # FAISS requires float32

    index.add(np.array([embedding]))  
    docs.append(text)

    save_store()


def get_all_docs():
    return docs