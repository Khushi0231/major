"""Chat Service - Configuration"""
import os


class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "chat")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8002"))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./dravis_chat.db",
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # LLM - Ollama (primary, local)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    # LLM - OpenAI (fallback, cloud)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # LLM - Groq (optional cloud, same models as Ollama, zero storage)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # Matches llama3.1:8b in Ollama

    # Inter-service
    DOCUMENT_SERVICE_URL: str = os.getenv("DOCUMENT_SERVICE_URL", "http://localhost:8003")


settings = Settings()
