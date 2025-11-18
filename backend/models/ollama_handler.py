import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama_handler")

MODEL_FILENAME = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

_llm = None

try:
    from llama_cpp import Llama

    if os.path.exists(MODEL_PATH):
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=4096,
            n_threads=6,
            n_batch=512,
            verbose=False
        )
        logger.info(f"Loaded GGUF model: {MODEL_PATH}")
    else:
        logger.error(f"Model file missing: {MODEL_PATH}")

except Exception as e:
    logger.exception("Failed to load llama_cpp model: %s", str(e))
    _llm = None


class OllamaHandler:
    def __init__(self):
        self.model = _llm

    def is_available(self):
        return self.model is not None

    def generate(self, prompt: str):
        if self.model is None:
            return None

        try:
            formatted_prompt = f"[INST] {prompt} [/INST]"

            output = self.model(
                prompt=formatted_prompt,
                max_tokens=512,
                temperature=0.5,
            )

            if isinstance(output, dict) and "choices" in output:
                return output["choices"][0]["text"].strip()

            return str(output).strip()

        except Exception as e:
            logger.exception("Generation error:", e)
            return None
