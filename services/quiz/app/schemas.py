"""Quiz Service - Pydantic schemas"""
from typing import Optional, List
from pydantic import BaseModel


class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    quiz_type: str = "simple"
    use_documents: bool = False


class QuizQuestion(BaseModel):
    type: str = "mcq"
    question: str
    options: List[str] = []
    correct_answer: str = ""
    explanation: str = ""


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    error: str = ""


class HealthResponse(BaseModel):
    status: str
    service: str
    chat_service: str = "unknown"
    document_service: str = "unknown"
