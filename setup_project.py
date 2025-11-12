import os
import json

# Backend Config
backend_config = {
    'config.py': '''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
VECTOR_DIR = DATA_DIR / "vectors"
MODEL_DIR = DATA_DIR / "models"
UPLOAD_DIR = DATA_DIR / "uploads"
CACHE_DIR = DATA_DIR / "cache"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Ollama Configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama2"  # Change to: mixtral, neural-chat, etc.
OLLAMA_EMBED_MODEL = "nomic-embed-text"

# API Configuration
API_HOST = "127.0.0.1"
API_PORT = 8000
API_RELOAD = True
API_LOG_LEVEL = "info"

# Database
DATABASE_URL = f"sqlite:///{ DATA_DIR}/dravis.db"

# ChromaDB
CHROMA_DB_PATH = str(VECTOR_DIR)
CHROMA_COLLECTION = "documents"

# Logging
LOG_FILE = LOG_DIR / "dravis.log"
LOG_LEVEL = "INFO"
'''
}

# Create backend files
for filename, content in backend_config.items():
    filepath = os.path.join('backend', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)

print("✓ Backend config files created")
