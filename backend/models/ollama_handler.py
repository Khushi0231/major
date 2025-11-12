
"""Ollama LLM Handler - Local model inference interface"""
import requests
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class OllamaHandler:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.available = self.check_available()
    
    def check_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return resp.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        if not self.available:
            return "[Ollama service not available]"
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "temperature": temperature}
            )
            return resp.json().get("response", "No response")
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"[Error: {str(e)}]"
    
    def embed(self, text: str) -> List[float]:
        try:
            resp = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text}
            )
            return resp.json().get("embedding", [])
        except:
            return []
