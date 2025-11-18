"""Language detection for text queries (English, Hindi, Hinglish)"""
import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Hindi Devanagari script range
DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')

# Common Hinglish/Roman Hindi keywords
HINGLISH_KEYWORDS = [
    'kya', 'hai', 'ko', 'ka', 'ki', 'ke', 'mein', 'se', 'par', 'aur', 'ya',
    'nahi', 'nahin', 'hain', 'ho', 'raha', 'rahi', 'rahe', 'tha', 'thi', 'the',
    'kab', 'kahan', 'kaise', 'kyun', 'kis', 'kisne', 'kisko', 'kiski'
]


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect language of input text.
    
    Returns:
        Tuple of (detected_language, confidence)
        Language can be: 'en' (English), 'hi' (Hindi), 'hinglish' (Hinglish)
    """
    if not text or not text.strip():
        return 'en', 0.0
    
    text_lower = text.lower().strip()
    
    # Check for Devanagari script (Hindi)
    devanagari_count = len(DEVANAGARI_PATTERN.findall(text))
    total_chars = len([c for c in text if c.isalpha()])
    
    if total_chars > 0:
        devanagari_ratio = devanagari_count / total_chars
        if devanagari_ratio > 0.3:  # More than 30% Devanagari characters
            return 'hi', min(devanagari_ratio, 1.0)
    
    # Check for Hinglish keywords
    hinglish_matches = sum(1 for keyword in HINGLISH_KEYWORDS if keyword in text_lower)
    word_count = len(text_lower.split())
    
    if word_count > 0:
        hinglish_ratio = hinglish_matches / word_count
        if hinglish_ratio > 0.15:  # More than 15% Hinglish keywords
            return 'hinglish', min(hinglish_ratio * 2, 1.0)
    
    # Default to English
    return 'en', 0.8


def should_respond_in_language(detected_lang: str, query: str) -> bool:
    """Determine if response should be in the detected language"""
    if detected_lang == 'hi':
        return True
    elif detected_lang == 'hinglish':
        # Respond in Hinglish if query has significant Hinglish content
        _, confidence = detect_language(query)
        return confidence > 0.3
    return False

