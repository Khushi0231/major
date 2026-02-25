"""Auth Service - Configuration"""
import os


class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "auth")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8001"))
    
    # In desktop mode, we default to SQLite in the current directory or a data folder
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./dravis_auth.db"
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
