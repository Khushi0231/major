"""Speech processing module"""
from .whisper_handler import transcribe_audio, detect_language, load_whisper_model

__all__ = ['transcribe_audio', 'detect_language', 'load_whisper_model']

