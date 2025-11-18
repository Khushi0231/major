import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # API Settings
    API_TITLE = "DRAVIS API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Dynamic Reasoning AI for Virtual Intelligent Study"
    
    # Server Settings
    HOST = os.getenv("API_HOST", "127.0.0.1")  # Changed to 127.0.0.1 for Windows
    PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Settings
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
    
    # Ollama Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))
    
    # Embedding Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    
    # Data Directory (Windows-compatible)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DRAVIS_DATA_DIR = os.path.join(BASE_DIR, "dravis_data")
    
    # Database Settings
    DB_PATH = os.getenv("DB_PATH", os.path.join(DRAVIS_DATA_DIR, "dravis.db"))
    CHROMA_PATH = os.getenv("CHROMA_PATH", os.path.join(DRAVIS_DATA_DIR, "chroma_db"))
    
    # Document Settings
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(DRAVIS_DATA_DIR, "uploads"))
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(1024 * 1024 * 1024)))  # 1GB
    ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "txt", "md", "jpg", "jpeg", "png", "bmp", "py", "java", "cpp", "js", "json"}
    
    # PIN Settings
    PIN_HASH_FILE = os.path.join(DRAVIS_DATA_DIR, "pin.hash")
    
    # Voice Settings
    TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")
    STT_ENGINE = os.getenv("STT_ENGINE", "wav2letter")
    
    # RAG Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.path.join(DRAVIS_DATA_DIR, "logs")
    LOG_FILE = os.getenv("LOG_FILE", os.path.join(LOG_DIR, "dravis.log"))
    
    @classmethod
    def ensure_directories(cls):
        """Create all necessary directories"""
        dirs = [cls.DRAVIS_DATA_DIR, cls.UPLOAD_DIR, cls.LOG_DIR, cls.CHROMA_PATH]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    @classmethod
    def get_config(cls) -> dict:
        """Return configuration as dictionary"""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and key.isupper()
        }
