"""LLM Manager - Handles provider selection and fallback"""
from typing import List, Optional, Dict, Any
from .providers import LLMProvider, OllamaProvider, OpenAIProvider, MockProvider, GGUFProvider
import logging
import asyncio

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages multiple LLM providers with fallback"""
    
    def __init__(self, config: dict):
        self.providers: List[LLMProvider] = []
        self.config = config
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize providers in priority order"""
        # Try Ollama first (free, local, best for Codespaces)
        if self.config.get("ollama", {}).get("enabled", True):
            try:
                provider = OllamaProvider(self.config.get("ollama", {}))
                self.providers.append(provider)
                logger.info("Ollama provider added")
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama: {e}")
        
        # Try GGUF model (local file, supports tar extraction)
        try:
            provider = GGUFProvider(self.config.get("gguf", {}))
            self.providers.append(provider)
            logger.info("GGUF provider added")
        except Exception as e:
            logger.warning(f"Failed to initialize GGUF: {e}")
        
        # Then OpenAI (cloud, costs money)
        if self.config.get("openai", {}).get("enabled", False):
            try:
                provider = OpenAIProvider(self.config.get("openai", {}))
                self.providers.append(provider)
                logger.info("OpenAI provider added")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Finally Mock (always works, for testing)
        if self.config.get("mock", {}).get("enabled", False):
            try:
                provider = MockProvider(self.config.get("mock", {}))
                self.providers.append(provider)
                logger.info("Mock provider added")
            except Exception as e:
                logger.warning(f"Failed to initialize Mock: {e}")
        
        if not self.providers:
            logger.error("No LLM providers initialized!")
            # Add mock as fallback
            self.providers.append(MockProvider({}))
        
        logger.info(f"Initialized {len(self.providers)} LLM providers")
    
    def is_available(self) -> bool:
        """Check if any real (non-mock) provider is available"""
        import requests
        for provider in self.providers:
            try:
                if isinstance(provider, MockProvider):
                    continue  # Don't count mock as "available"
                if isinstance(provider, GGUFProvider):
                    if provider.model is not None:
                        return True
                if isinstance(provider, OllamaProvider):
                    try:
                        r = requests.get(f"{provider.base_url}/api/tags", timeout=2)
                        if r.status_code == 200:
                            return True
                    except:
                        continue
                if isinstance(provider, OpenAIProvider):
                    return True  # If configured, assume available
            except:
                continue
        return False
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate response using first available provider (synchronous wrapper)"""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            # We're inside an event loop (FastAPI), create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(self._sync_generate, prompt, **kwargs)
                return future.result(timeout=60)
        else:
            # No event loop running, create one
            return asyncio.run(self._async_generate(prompt, **kwargs))
    
    def _sync_generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Run async generate in a new event loop (for thread execution)"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._async_generate(prompt, **kwargs))
        finally:
            loop.close()
    
    async def _async_generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate response using first available provider"""
        errors = []
        
        for provider in self.providers:
            try:
                is_available = await provider.is_available()
                if is_available:
                    logger.info(f"Using provider: {provider.name}")
                    response = await provider.generate(prompt, **kwargs)
                    return response
                else:
                    msg = f"{provider.name} not available"
                    logger.debug(msg)
                    errors.append(msg)
            except Exception as e:
                msg = f"{provider.name}: {str(e)}"
                logger.warning(f"Provider failed: {msg}")
                errors.append(msg)
                continue
        
        # No provider worked
        error_msg = f"All LLM providers failed. Errors: {'; '.join(errors)}"
        logger.error(error_msg)
        return None
    
    async def generate_async(self, prompt: str, **kwargs) -> dict:
        """Generate response using first available provider (async version)"""
        errors = []
        
        for provider in self.providers:
            try:
                is_available = await provider.is_available()
                if is_available:
                    logger.info(f"Using provider: {provider.name}")
                    response = await provider.generate(prompt, **kwargs)
                    return {
                        "response": response,
                        "provider": provider.name,
                        "model_info": provider.get_model_info()
                    }
                else:
                    msg = f"{provider.name} not available"
                    logger.debug(msg)
                    errors.append(msg)
            except Exception as e:
                msg = f"{provider.name}: {str(e)}"
                logger.warning(f"Provider failed: {msg}")
                errors.append(msg)
                continue
        
        # No provider worked
        error_msg = f"All LLM providers failed. Errors: {'; '.join(errors)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    async def health_check(self) -> dict:
        """Check health of all providers"""
        results = {}
        for provider in self.providers:
            try:
                results[provider.name] = await provider.health_check()
            except Exception as e:
                results[provider.name] = {
                    "provider": provider.name,
                    "status": "error",
                    "error": str(e)
                }
        return results
