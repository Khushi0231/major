
"""Custom error handling"""
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    detail: str = None

class DRAVISException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
