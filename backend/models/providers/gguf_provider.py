"""GGUF Provider - Local GGUF model with tar compression support"""
import os
import tarfile
import glob
import logging
from typing import Dict, Any
from .base import LLMProvider

logger = logging.getLogger(__name__)

# Paths - this file is at backend/models/providers/gguf_provider.py
# So we go up one level to get to backend/models/
MODELS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_gguf_model() -> str:
    """
    Find a GGUF model in the models directory.
    If only a .tar or .tar.gz is found, extract it first.
    """
    # 1. Look for existing .gguf files
    gguf_files = glob.glob(os.path.join(MODELS_DIR, "*.gguf"))
    if gguf_files:
        logger.info(f"Found GGUF model: {gguf_files[0]}")
        return gguf_files[0]
    
    # 2. Look for tar-compressed models and extract
    tar_patterns = ["*.tar", "*.tar.gz", "*.tgz", "*.tar.bz2"]
    for pattern in tar_patterns:
        tar_files = glob.glob(os.path.join(MODELS_DIR, pattern))
        for tar_path in tar_files:
            logger.info(f"Found tar archive: {tar_path}, extracting...")
            try:
                with tarfile.open(tar_path, "r:*") as tar:
                    # Extract only .gguf files
                    gguf_members = [m for m in tar.getmembers() if m.name.endswith('.gguf')]
                    if gguf_members:
                        for member in gguf_members:
                            # Extract to the models directory with flat structure
                            member.name = os.path.basename(member.name)
                            tar.extract(member, MODELS_DIR)
                            extracted_path = os.path.join(MODELS_DIR, member.name)
                            logger.info(f"Extracted GGUF model: {extracted_path}")
                            return extracted_path
                    else:
                        # Extract everything and search again
                        tar.extractall(MODELS_DIR)
                        gguf_files = glob.glob(os.path.join(MODELS_DIR, "**/*.gguf"), recursive=True)
                        if gguf_files:
                            logger.info(f"Found GGUF after extraction: {gguf_files[0]}")
                            return gguf_files[0]
            except Exception as e:
                logger.warning(f"Failed to extract {tar_path}: {e}")
    
    return ""


class GGUFProvider(LLMProvider):
    """Local GGUF model provider using llama-cpp-python"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.model_path = config.get("model_path", "") or _find_gguf_model()
        self.n_ctx = config.get("n_ctx", 4096)
        self.n_threads = config.get("n_threads", 4)
        self.n_batch = config.get("n_batch", 512)
        
        if self.model_path and os.path.exists(self.model_path):
            self._load_model()
        else:
            logger.info("No GGUF model found. GGUF provider will be unavailable.")
    
    def _load_model(self):
        """Load the GGUF model"""
        try:
            from llama_cpp import Llama
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_batch=self.n_batch,
                verbose=False
            )
            logger.info(f"✓ Loaded GGUF model: {os.path.basename(self.model_path)}")
        except ImportError:
            logger.warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load GGUF model: {e}")
            self.model = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using local GGUF model"""
        if self.model is None:
            raise Exception("GGUF model not loaded")
        
        try:
            formatted_prompt = f"[INST] {prompt} [/INST]"
            
            output = self.model(
                prompt=formatted_prompt,
                max_tokens=kwargs.get("max_tokens", 512),
                temperature=kwargs.get("temperature", 0.5),
            )
            
            if isinstance(output, dict) and "choices" in output:
                return output["choices"][0]["text"].strip()
            
            return str(output).strip()
        except Exception as e:
            logger.error(f"GGUF generation error: {e}")
            raise Exception(f"GGUF generation failed: {str(e)}")
    
    async def is_available(self) -> bool:
        """Check if GGUF model is loaded"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return GGUF model info"""
        return {
            "provider": "gguf",
            "model": os.path.basename(self.model_path) if self.model_path else "none",
            "type": "local",
            "loaded": self.model is not None,
            "n_ctx": self.n_ctx,
            "n_threads": self.n_threads
        }
