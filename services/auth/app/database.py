"""Auth Service - Database models and session management"""
import logging
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PinModel(Base):
    """PIN storage - only one active PIN at a time"""
    __tablename__ = "auth_pins"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    pin_hash   = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
    )


def get_db():
    """FastAPI dependency: yields a DB session, auto-closes after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_tables():
    """Create tables if they don't exist (safe to call repeatedly)."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Auth tables verified/created")
    except Exception as e:
        logger.error(f"Failed to init auth tables: {e}")
