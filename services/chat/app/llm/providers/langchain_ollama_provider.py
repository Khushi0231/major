"""LangChain + Ollama Provider — Primary LLM engine for DRAVIS

Uses LangChain's ChatOllama with a strong system prompt to ensure
professional, helpful, and accurate AI study assistant responses.
"""
import logging
from typing import Dict, Any
import requests
from .base import LLMProvider

logger = logging.getLogger(__name__)

# ── System prompt ── injected on every call ──────────────────────────────
SYSTEM_PROMPT = """You are DRAVIS, a professional AI study assistant built to help students learn better.

Your behaviour:
- Always respond clearly, accurately, and professionally
- Structure answers with headings, bullet points, or numbered lists when it helps readability
- For study/academic topics: give thorough, well-explained answers with examples
- For simple questions: keep it concise but complete — no unnecessary padding
- If given document context, ground your answer in that context first, then supplement with your knowledge
- Never say "As an AI…" or "I cannot…" — just answer helpfully
- If you don't know something, say so honestly and suggest how the user can find out
- Maintain a warm, encouraging, professional tone — you are a knowledgeable tutor

You support English, Hindi, and Hinglish. Detect the language from the user message and respond in the same language.""".strip()


class LangChainOllamaProvider(LLMProvider):
    """Primary LLM provider using LangChain + Ollama (llama3.1:8b) for local inference."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.1:8b")
        self.timeout = config.get("timeout", 120)
        self.temperature = config.get("temperature", 0.6)
        self._llm = None

    def _get_llm(self, num_predict: int = 2048):
        """Return a ChatOllama instance (re-initialised if token count differs)."""
        if self._llm is not None and self._llm.num_predict == num_predict:
            return self._llm
        try:
            from langchain_ollama import ChatOllama
            self._llm = ChatOllama(
                base_url=self.base_url,
                model=self.model,
                temperature=self.temperature,
                num_predict=num_predict,
                top_p=0.9,
                repeat_penalty=1.1,
            )
            logger.info(f"LangChain+Ollama ready: model={self.model} @ {self.base_url}")
            return self._llm
        except ImportError:
            logger.error("langchain-ollama not installed. Run: pip install langchain-ollama")
            raise
        except Exception as e:
            logger.error(f"Failed to init LangChain+Ollama: {e}")
            raise

    def generate(self, prompt: str, **kwargs) -> str:
        max_tokens = kwargs.get("max_tokens", 2048)
        llm = self._get_llm(num_predict=max_tokens)

        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
            # invoke() takes only messages — params are set on the model object
            response = llm.invoke(messages)
            text = response.content.strip()
            if not text:
                raise RuntimeError("Empty response from LLM")
            return text
        except Exception as e:
            raise RuntimeError(f"LangChain+Ollama generation failed: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is running AND the target model is present."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            model_base = self.model.split(":")[0]
            return any(model_base in m for m in models)
        except Exception:
            return False

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "langchain_ollama",
            "model": self.model,
            "type": "local",
            "framework": "langchain",
            "base_url": self.base_url,
        }
