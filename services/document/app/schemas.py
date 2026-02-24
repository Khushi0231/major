"""Document Service - Pydantic schemas"""
from typing import Optional, List
from pydantic import BaseModel


class DocumentInfo(BaseModel):
    document_id: str
    document_name: str
    file_size: int = 0
    chunk_count: int = 0
    status: str = "processing"
    created_at: str = ""


class UploadResponse(BaseModel):
    success: bool
    document_id: str = ""
    filename: str = ""
    chunks: int = 0
    file_size: int = 0
    error: str = ""


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]


class DeleteResponse(BaseModel):
    success: bool
    message: str = ""


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


class QueryResult(BaseModel):
    text: str
    metadata: dict = {}
    distance: Optional[float] = None


class QueryResponse(BaseModel):
    results: List[QueryResult]


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str = "unknown"
    chromadb: str = "unknown"
    embedding_model: str = ""
