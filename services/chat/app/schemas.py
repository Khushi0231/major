"""Chat Service - Pydantic schemas"""
from typing import Optional, List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    use_documents: bool = False
    mode: str = "normal"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    language: str = "en"
    mode: str = "normal"
    provider: str = ""
    error: str = ""


class GenerateRequest(BaseModel):
    """Internal endpoint for other services (e.g. Quiz) to use LLM."""
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    response: str
    provider: str = ""


class HistoryItem(BaseModel):
    id: int
    session_id: str
    user_message: str
    assistant_response: str
    use_rag: bool
    mode: str
    language: Optional[str]
    provider: Optional[str]
    created_at: str


class HistoryResponse(BaseModel):
    messages: List[HistoryItem]
    total: int


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str = "unknown"
    llm_providers: dict = {}
