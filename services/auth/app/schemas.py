"""Auth Service - Pydantic request/response schemas"""
from pydantic import BaseModel, field_validator


class PinSetRequest(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        if not v or len(v) != 4 or not v.isdigit():
            raise ValueError("PIN must be exactly 4 digits")
        return v


class PinVerifyRequest(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        if not v or len(v) != 4 or not v.isdigit():
            raise ValueError("PIN must be exactly 4 digits")
        return v


class PinSetResponse(BaseModel):
    success: bool
    message: str = ""


class PinVerifyResponse(BaseModel):
    verified: bool
    error: str = ""


class PinExistsResponse(BaseModel):
    exists: bool


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str = "unknown"
