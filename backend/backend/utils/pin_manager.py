import hashlib
from pathlib import Path

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def save_pin_hash(pin_hash_file: str, pin: str):
    hashed = hash_pin(pin)
    Path(pin_hash_file).write_text(hashed)
    return True

def verify_pin(pin_hash_file: str, pin: str):
    p = Path(pin_hash_file)
    if not p.exists():
        return False
    stored = p.read_text().strip()
    return stored == hash_pin(pin)

def pin_exists(pin_hash_file: str):
    return Path(pin_hash_file).exists()
