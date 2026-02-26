"""Document Service - Configuration"""
import os


class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "document")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8003"))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./dravis_docs.db",
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ChromaDB — server mode (Docker) or local persistence (desktop)
    CHROMADB_HOST: str = os.getenv("CHROMADB_HOST", "")
    CHROMADB_PORT: int = int(os.getenv("CHROMADB_PORT", "8000"))
    # Only use local persistence if CHROMADB_HOST is NOT set (i.e., desktop mode)
    CHROMADB_PERSIST_DIR: str = os.getenv("CHROMADB_PERSIST_DIR", "") if os.getenv("CHROMADB_HOST") else os.getenv("CHROMADB_PERSIST_DIR", "./chroma_db")

    # Upload limits
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    ALLOWED_EXTENSIONS: set = {"pdf", "docx", "pptx", "txt", "md", "jpg", "jpeg", "png"}

    # Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Embedding model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


settings = Settings()

