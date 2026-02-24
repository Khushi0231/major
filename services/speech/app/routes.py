"""Speech Service - API Routes"""
import os
import uuid
import logging
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from pydantic import BaseModel
from .config import settings
from . import whisper_handler

logger = logging.getLogger(__name__)
router = APIRouter()


class TranscribeResponse(BaseModel):
    text: str
    language: str = "unknown"
    success: bool = True


class HealthResponse(BaseModel):
    status: str
    service: str
    whisper_model: str = ""
    model_ready: bool = False


@router.post("/transcribe", response_model=TranscribeResponse)
def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None),
):
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    temp_path = os.path.join(settings.TEMP_DIR, f"temp_{uuid.uuid4()}.wav")

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)

        text, detected_lang = whisper_handler.transcribe(temp_path, language=language)
        return TranscribeResponse(text=text, language=detected_lang)

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(500, f"Speech-to-text failed: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/health", response_model=HealthResponse)
def health_check():
    ready = whisper_handler.is_ready()
    return HealthResponse(
        status="ok" if ready else "degraded",
        service="speech",
        whisper_model=settings.WHISPER_MODEL,
        model_ready=ready,
    )
