"""Configuration management"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, env vars must be set manually

class Config:
    """Application configuration"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    CHROMA_PATH = os.getenv("CHROMA_PATH", str(BASE_DIR / ".." / "chroma_db"))
    DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / ".." / "dravis_data" / "dravis.db"))
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / ".." / "dravis_data" / "uploads"))
    LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / ".." / "dravis_data" / "logs"))
    LOG_FILE = os.path.join(LOG_DIR, "dravis.log")
    PIN_HASH_FILE = os.path.join(str(BASE_DIR / ".." / "dravis_data"), "pin_hash.txt")
    
    # API Configuration
    API_TITLE = "DRAVIS API"
    API_VERSION = "1.0.0"
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Aliases used by main.py
    HOST = API_HOST
    PORT = API_PORT
    
    # File upload settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    ALLOWED_EXTENSIONS = {
        'pdf', 'docx', 'pptx', 'txt', 'md',
        'jpg', 'jpeg', 'png', 'bmp',
        'py', 'java', 'cpp', 'js', 'json'
    }
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # RAG Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # LLM Providers
    LLM_CONFIG = {
        "ollama": {
            "enabled": os.getenv("OLLAMA_ENABLED", "true").lower() == "true",
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "mistral"),
            "timeout": int(os.getenv("OLLAMA_TIMEOUT", "120"))
        },
        "gguf": {
            "model_dir": os.getenv("GGUF_MODEL_DIR", str(BASE_DIR / "models")),
        },
        "openai": {
            "enabled": os.getenv("OPENAI_ENABLED", "false").lower() == "true",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        },
        "mock": {
            "enabled": os.getenv("MOCK_ENABLED", "true").lower() == "true"
        }
    }
    
    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        for directory in [Config.UPLOAD_DIR, Config.LOG_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)
        # Ensure chroma_db directory
        Path(Config.CHROMA_PATH).mkdir(parents=True, exist_ok=True)
        # Ensure database directory
        Path(Config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

config = Config()
