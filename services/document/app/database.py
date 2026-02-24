"""Document Service - Database models"""
import logging
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5, max_overflow=10, pool_recycle=3600, pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DocumentRecord(Base):
    __tablename__ = "documents"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    document_id   = Column(String(36), unique=True, nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    file_path     = Column(String(500), nullable=True)
    file_size     = Column(Integer, default=0)
    chunk_count   = Column(Integer, default=0)
    status        = Column(String(20), default="processing")
    created_at    = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Document tables verified/created")
    except Exception as e:
        logger.error(f"Failed to init document tables: {e}")
