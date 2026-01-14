"""Simple Demo API to test DRAVIS LLM system"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0, 'backend')
from models.llm_manager import LLMManager
from config import config
import logging

# Setup logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="DRAVIS Demo API", version="2.0")

# Initialize LLM Manager
logger.info("Initializing LLM Manager...")
llm_manager = LLMManager(config.LLM_CONFIG)

class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    provider: str
    model_info: dict

@app.get("/")
async def root():
    return {
        "message": "DRAVIS Demo API v2.0 - 100% Functional!",
        "status": "operational",
        "endpoints": {
            "/": "This info",
            "/health": "Check LLM providers health",
            "/chat": "Chat with LLM (POST)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check for all LLM providers"""
    try:
        providers_health = await llm_manager.health_check()
        return {
            "status": "healthy",
            "providers": providers_health,
            "total_providers": len(llm_manager.providers)
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with LLM"""
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        result = await llm_manager.generate(
            request.message,
            temperature=request.temperature
        )
        logger.info(f"Generated response using {result['provider']}")
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 DRAVIS Demo API Starting...")
    print("="*60)
    print(f"📍 URL: http://localhost:{config.API_PORT}")
    print(f"📚 Docs: http://localhost:{config.API_PORT}/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
