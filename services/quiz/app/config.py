"""Quiz Service - Configuration"""
import os


class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "quiz")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8004"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CHAT_SERVICE_URL: str = os.getenv("CHAT_SERVICE_URL", "http://localhost:8002")
    DOCUMENT_SERVICE_URL: str = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8003")


settings = Settings()
