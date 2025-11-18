"""4-digit PIN management with SHA-256 hashing"""
import hashlib
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def hash_pin(pin: str) -> str:
    """Hash a 4-digit PIN using SHA-256"""
    if not pin or len(pin) != 4 or not pin.isdigit():
        raise ValueError("PIN must be exactly 4 digits")
    
    return hashlib.sha256(pin.encode()).hexdigest()


def save_pin_hash(pin: str, hash_file: str):
    """Save hashed PIN to file"""
    pin_hash = hash_pin(pin)
    os.makedirs(os.path.dirname(hash_file), exist_ok=True)
    
    with open(hash_file, 'w') as f:
        f.write(pin_hash)
    
    logger.info("PIN hash saved")


def verify_pin(pin: str, hash_file: str) -> bool:
    """Verify a PIN against stored hash"""
    if not os.path.exists(hash_file):
        return False
    
    try:
        with open(hash_file, 'r') as f:
            stored_hash = f.read().strip()
        
        input_hash = hash_pin(pin)
        return input_hash == stored_hash
    except Exception as e:
        logger.error(f"PIN verification failed: {e}")
        return False


def pin_exists(hash_file: str) -> bool:
    """Check if PIN is already set"""
    return os.path.exists(hash_file) and os.path.getsize(hash_file) > 0

