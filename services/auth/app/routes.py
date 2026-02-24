"""Auth Service - API Routes"""
import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db, PinModel, engine
from .schemas import (
    PinSetRequest, PinSetResponse,
    PinVerifyRequest, PinVerifyResponse,
    PinExistsResponse, HealthResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _hash_pin(pin: str) -> str:
    """SHA-256 hash of the PIN."""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


# ─── PIN Management ─────────────────────────────

@router.post("/pin/set", response_model=PinSetResponse)
def set_pin(req: PinSetRequest, db: Session = Depends(get_db)):
    """Set or replace the application PIN."""
    pin_hash = _hash_pin(req.pin)

    # Upsert: delete old, insert new (only one PIN at a time)
    db.query(PinModel).delete()
    db.add(PinModel(pin_hash=pin_hash))
    db.commit()

    logger.info("PIN set successfully")
    return PinSetResponse(success=True, message="PIN saved successfully")


@router.post("/pin/verify", response_model=PinVerifyResponse)
def verify_pin(req: PinVerifyRequest, db: Session = Depends(get_db)):
    """Verify a PIN against stored hash."""
    record = db.query(PinModel).order_by(PinModel.id.desc()).first()
    if not record:
        raise HTTPException(status_code=404, detail="No PIN has been set")

    input_hash = _hash_pin(req.pin)
    if input_hash == record.pin_hash:
        return PinVerifyResponse(verified=True)
    return PinVerifyResponse(verified=False, error="Invalid PIN")


@router.get("/pin/exists", response_model=PinExistsResponse)
def check_pin_exists(db: Session = Depends(get_db)):
    """Check whether a PIN has been configured."""
    count = db.query(PinModel).count()
    return PinExistsResponse(exists=count > 0)


# ─── Health ─────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Deep health check including database connectivity."""
    db_status = "unknown"
    try:
        from sqlalchemy import text as sa_text
        with engine.connect() as conn:
            conn.execute(sa_text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        service="auth",
        database=db_status,
    )
