"""Unified LLM Manager - Uses Ollama if available, falls back to local llama-cpp"""
import logging
import time
import requests
from typing import Optional, Tuple
from .ollama_handler import OllamaHandler as LocalLLMHandler

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        self.local_llm = LocalLLMHandler()
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_model = "mistral:7b"  # Default Ollama model
        self.ollama_available = False
        self.preferred_backend = None
        
        # Check which backends are available
        self._check_availability()
    
    def _check_availability(self):
        """Check which LLM backends are available"""
        # Check Ollama
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    # Filter out embedding-only models
                    chat_models = [m for m in models if m.get("name", "").lower() not in ["nomic-embed-text:latest"]]
                    
                    if chat_models:
                        # Try to find best model in priority order
                        priority_models = ["llama3.1", "llama3", "mistral", "phi", "neural-chat"]
                        best_model = None
                        
                        for priority in priority_models:
                            candidates = [m for m in chat_models if priority in m.get("name", "").lower()]
                            if candidates:
                                # Use the full model name from the list
                                best_model = candidates[0]["name"]
                                break
                        
                        # If no priority match, use first chat model
                        if not best_model:
                            best_model = chat_models[0]["name"]
                        
                        self.ollama_model = best_model
                        self.ollama_available = True
                        logger.info(f"✓ Ollama available with model: {self.ollama_model}")
                    else:
                        logger.warning("⚠ Ollama has no chat models (only embeddings)")
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            self.ollama_available = False
        
        # Check local LLM
        local_available = self.local_llm.is_available()
        if local_available:
            logger.info("✓ Local GGUF model available")
        
        # Prefer Ollama if both available (usually more reliable)
        if self.ollama_available:
            self.preferred_backend = "ollama"
            logger.info("→ Using Ollama as primary LLM backend")
        elif local_available:
            self.preferred_backend = "local"
            logger.info("→ Using local GGUF model as LLM backend")
        else:
            self.preferred_backend = None
            logger.warning("✗ No LLM backend available! Please:")
            logger.warning("  1. Install Ollama from https://ollama.ai")
            logger.warning("  2. Run: ollama pull mistral:7b")
            logger.warning("  3. Make sure Ollama is running on port 11434")
    
    def is_available(self) -> bool:
        """Check if any LLM backend is available"""
        return self.ollama_available or self.local_llm.is_available()
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """
        Generate response using available backend.
        Tries local first (faster/more reliable), then Ollama.
        """
        if not self.is_available():
            logger.warning("No LLM backend available!")
            return None
        
        # Try local first (usually faster and more reliable)
        if self.local_llm.is_available():
            try:
                result = self._generate_local(prompt, max_tokens, temperature)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Local LLM failed, trying Ollama: {e}")
        
        # Fall back to Ollama
        if self.ollama_available:
            try:
                result = self._generate_ollama(prompt, max_tokens, temperature)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Ollama failed: {e}")
        
        logger.error("All LLM backends failed")
        return None
    
    def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate using Ollama API"""
        try:
            # Format prompt for Mistral
            formatted_prompt = f"[INST] {prompt} [/INST]"
            
            payload = {
                "model": self.ollama_model,
                "prompt": formatted_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=120  # 2 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                elapsed = time.time() - start_time
                logger.info(f"Ollama response generated in {elapsed:.2f}s")
                return response_text
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.warning("Ollama request timed out")
            return None
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return None
    
    def _generate_local(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate using local llama-cpp"""
        try:
            start_time = time.time()
            result = self.local_llm.generate(prompt)
            if result:
                elapsed = time.time() - start_time
                logger.info(f"Local LLM response generated in {elapsed:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            return None

