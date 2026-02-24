"""Language detection for English / Hindi / Hinglish"""
import re
from typing import Tuple

DEVANAGARI = re.compile(r"[\u0900-\u097F]")

HINGLISH_KEYWORDS = {
    "kya", "hai", "ko", "ka", "ki", "ke", "mein", "se", "par", "aur", "ya",
    "nahi", "nahin", "hain", "ho", "raha", "rahi", "rahe", "tha", "thi",
    "kab", "kahan", "kaise", "kyun", "kis", "kisne",
}


def detect_language(text: str) -> Tuple[str, float]:
    """Return (language_code, confidence).  language_code ∈ {en, hi, hinglish}."""
    if not text or not text.strip():
        return "en", 0.0

    alpha_chars = [c for c in text if c.isalpha()]
    total = len(alpha_chars) or 1

    # Check Devanagari
    dev_count = len(DEVANAGARI.findall(text))
    if dev_count / total > 0.3:
        return "hi", min(dev_count / total, 1.0)

    # Check Hinglish keywords
    words = text.lower().split()
    matches = sum(1 for w in words if w in HINGLISH_KEYWORDS)
    if words and matches / len(words) > 0.15:
        return "hinglish", min(matches / len(words) * 2, 1.0)

    return "en", 0.8
