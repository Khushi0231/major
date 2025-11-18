"""Whisper speech-to-text handler"""
import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

_whisper_model = None

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("OpenAI Whisper not available")

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False


def load_whisper_model(model_size: str = "base"):
    """Load Whisper model (prefer faster-whisper if available)"""
    global _whisper_model
    
    if _whisper_model is not None:
        return _whisper_model
    
    if FASTER_WHISPER_AVAILABLE:
        try:
            _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info(f"Loaded faster-whisper model: {model_size}")
            return _whisper_model
        except Exception as e:
            logger.warning(f"Failed to load faster-whisper: {e}, trying openai-whisper")
    
    if WHISPER_AVAILABLE:
        try:
            _whisper_model = whisper.load_model(model_size)
            logger.info(f"Loaded OpenAI Whisper model: {model_size}")
            return _whisper_model
        except Exception as e:
            logger.error(f"Failed to load OpenAI Whisper: {e}")
    
    return None


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: Optional[str] = None
) -> Tuple[str, str]:
    """
    Transcribe audio file to text.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Optional language code (e.g., 'en', 'hi')
    
    Returns:
        Tuple of (transcribed_text, detected_language)
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    model = load_whisper_model(model_size)
    if model is None:
        raise Exception("Whisper model not available")
    
    try:
        # Use faster-whisper if available
        if FASTER_WHISPER_AVAILABLE and isinstance(model, WhisperModel):
            segments, info = model.transcribe(
                audio_path,
                language=language,
                beam_size=5
            )
            text = " ".join([segment.text for segment in segments])
            detected_lang = info.language
            return text.strip(), detected_lang
        
        # Fallback to OpenAI Whisper
        if WHISPER_AVAILABLE:
            result = model.transcribe(audio_path, language=language)
            text = result["text"]
            detected_lang = result.get("language", "unknown")
            return text.strip(), detected_lang
        
        raise Exception("No Whisper implementation available")
    
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise


def detect_language(audio_path: str, model_size: str = "base") -> str:
    """Detect language from audio file"""
    try:
        _, language = transcribe_audio(audio_path, model_size=model_size)
        return language
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return "unknown"

