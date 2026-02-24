"""Speech Service - Configuration"""
import os


class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "speech")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8005"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/dravis_audio")


settings = Settings()
