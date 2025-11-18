"""SQLite database management for chat history and settings"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLiteManager:
    def __init__(self, db_path: str = "dravis_data/dravis.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                use_rag BOOLEAN DEFAULT 0,
                mode TEXT DEFAULT 'normal',
                language TEXT
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def add_message(
        self,
        user_msg: str,
        asst_msg: str,
        use_rag: bool = False,
        mode: str = "normal",
        language: Optional[str] = None
    ):
        """Add a chat message to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO chat_history 
               (user_message, assistant_response, timestamp, use_rag, mode, language) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_msg, asst_msg, datetime.now().isoformat(), use_rag, mode, language)
        )
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_message, assistant_response, timestamp, use_rag, mode, language 
               FROM chat_history 
               ORDER BY id DESC 
               LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": r[0],
                "user": r[1],
                "assistant": r[2],
                "time": r[3],
                "rag": bool(r[4]),
                "mode": r[5] or "normal",
                "language": r[6]
            }
            for r in rows
        ]
    
    def clear_history(self):
        """Clear all chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history")
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()
        conn.close()
