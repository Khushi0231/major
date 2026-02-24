"""Auth Service - Configuration"""
import os


class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "auth")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8001"))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://dravis:dravis_pass_2024@localhost:3306/dravis"
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
