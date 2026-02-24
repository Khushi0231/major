"""Chat Service - Database models and session management"""
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP, text
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


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    session_id         = Column(String(64), nullable=False, index=True)
    user_message       = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    use_rag            = Column(Boolean, default=False)
    mode               = Column(String(20), default="normal")
    language           = Column(String(10), nullable=True)
    provider           = Column(String(50), nullable=True)
    created_at         = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class ChatSetting(Base):
    __tablename__ = "chat_settings"

    setting_key   = Column(String(100), primary_key=True)
    setting_value = Column(Text, nullable=False)
    updated_at    = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Chat tables verified/created")
    except Exception as e:
        logger.error(f"Failed to init chat tables: {e}")
