
"""Parse various document formats"""
import os
from typing import List, Dict
from pathlib import Path

class DocumentParser:
    @staticmethod
    def parse(file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == ".txt":
            with open(file_path, "r") as f:
                return f.read()
        elif ext == ".md":
            with open(file_path, "r") as f:
                return f.read()
        else:
            return f"[Parsing {ext} files not yet implemented]"
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i+chunk_size]))
        return chunks
