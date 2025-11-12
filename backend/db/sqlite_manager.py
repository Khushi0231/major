
"""SQLite database management for chat history"""
import sqlite3
from datetime import datetime
from typing import List, Dict
from pathlib import Path

class SQLiteManager:
    def __init__(self, db_path: str = "data/dravis.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                user_message TEXT,
                assistant_response TEXT,
                timestamp DATETIME,
                use_rag BOOLEAN
            )
        """)
        conn.commit()
        conn.close()
    
    def add_message(self, user_msg: str, asst_msg: str, use_rag: bool = False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_message, assistant_response, timestamp, use_rag) VALUES (?, ?, ?, ?)",
            (user_msg, asst_msg, datetime.now().isoformat(), use_rag)
        )
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "user": r[1], "assistant": r[2], "time": r[3], "rag": r[4]} for r in rows]
