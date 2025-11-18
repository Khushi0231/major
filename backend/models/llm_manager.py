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
                    # Try to find mistral or use first available
                    mistral_models = [m for m in models if "mistral" in m.get("name", "").lower()]
                    if mistral_models:
                        self.ollama_model = mistral_models[0]["name"]
                    else:
                        # Try common model names
                        common_models = ["mistral:7b", "llama2", "llama3", "phi"]
                        found = False
                        for common in common_models:
                            if any(common.split(":")[0] in m.get("name", "").lower() for m in models):
                                self.ollama_model = common
                                found = True
                                break
                        if not found:
                            self.ollama_model = models[0]["name"]
                    self.ollama_available = True
                    logger.info(f"Ollama available with model: {self.ollama_model}")
                else:
                    # No models, try to pull mistral
                    logger.info("Ollama available but no models. Attempting to pull mistral:7b...")
                    try:
                        pull_response = requests.post(
                            f"{self.ollama_base_url}/api/pull",
                            json={"name": "mistral:7b"},
                            timeout=300  # 5 minutes for model download
                        )
                        if pull_response.status_code == 200:
                            self.ollama_model = "mistral:7b"
                            self.ollama_available = True
                            logger.info("Successfully pulled mistral:7b model")
                    except:
                        logger.warning("Could not pull model automatically")
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            self.ollama_available = False
        
        # Check local LLM
        local_available = self.local_llm.is_available()
        
        # Prefer Ollama if both available (usually faster)
        if self.ollama_available:
            self.preferred_backend = "ollama"
            logger.info("Using Ollama as primary LLM backend")
        elif local_available:
            self.preferred_backend = "local"
            logger.info("Using local llama-cpp as LLM backend")
        else:
            self.preferred_backend = None
            logger.warning("No LLM backend available")
    
    def is_available(self) -> bool:
        """Check if any LLM backend is available"""
        return self.ollama_available or self.local_llm.is_available()
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """
        Generate response using fastest available backend.
        Uses concurrent requests to get the fastest response.
        """
        if not self.is_available():
            return None
        
        import concurrent.futures
        
        # Try both backends concurrently and return the first result
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            
            # Start Ollama if available
            if self.ollama_available:
                futures['ollama'] = executor.submit(self._generate_ollama, prompt, max_tokens, temperature)
            
            # Start local LLM if available
            if self.local_llm.is_available():
                futures['local'] = executor.submit(self._generate_local, prompt, max_tokens, temperature)
            
            # Wait for first successful result
            for future in concurrent.futures.as_completed(futures.values(), timeout=60):
                try:
                    result = future.result(timeout=0.1)
                    if result:
                        # Cancel other futures
                        for f in futures.values():
                            f.cancel()
                        return result
                except Exception as e:
                    logger.debug(f"One backend failed: {e}")
                    continue
        
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

