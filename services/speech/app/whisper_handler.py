"""Speech Service - Whisper STT handler"""
import os
import logging
from typing import Tuple
from .config import settings

logger = logging.getLogger(__name__)

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    try:
        import whisper
        _model = whisper.load_model(settings.WHISPER_MODEL)
        logger.info(f"Loaded Whisper model: {settings.WHISPER_MODEL}")
        return _model
    except Exception as e:
        logger.error(f"Failed to load Whisper: {e}")
        return None


def transcribe(audio_path: str, language: str = None) -> Tuple[str, str]:
    """Transcribe audio file. Returns (text, detected_language)."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = _load_model()
    if model is None:
        raise RuntimeError("Whisper model not available")

    result = model.transcribe(audio_path, language=language)
    text = result.get("text", "").strip()
    lang = result.get("language", "unknown")
    return text, lang


def is_ready() -> bool:
    return _load_model() is not None
