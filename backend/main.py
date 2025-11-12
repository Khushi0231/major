from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from pathlib import Path
from typing import List, Optional

from config import (
    API_HOST, API_PORT, API_LOG_LEVEL,
    UPLOAD_DIR, LOG_DIR, LOG_FILE
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, API_LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="DRAVIS",
    description="Offline Claude-Style Intelligent Study Assistant",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint"""
    return {"status": "operational", "service": "DRAVIS Backend"}

@app.post("/chat")
async def chat(message: str, use_rag: bool = False, context: Optional[str] = None):
    """Process chat message with optional RAG"""
    try:
        logger.info(f"Processing message: {message[:50]}...")
        # TODO: Implement RAG and LLM integration
        return {
            "response": f"Echo: {message}",
            "citations": [],
            "confidence": 0.8
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process documents"""
    try:
        logger.info(f"Uploading file: {file.filename}")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        filepath = UPLOAD_DIR / file.filename
        
        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # TODO: Parse file and add to vector store
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(contents)
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-docs")
async def list_documents():
    """List all indexed documents"""
    try:
        files = list(UPLOAD_DIR.glob("*"))
        return {"documents": [f.name for f in files]}
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts")
async def text_to_speech(text: str):
    """Convert text to speech"""
    try:
        logger.info(f"Converting text to speech: {text[:50]}...")
        # TODO: Implement Piper TTS
        return {
            "status": "success",
            "audio_url": "/audio/output.wav"
        }
    except Exception as e:
        logger.error(f"Error in TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech to text"""
    try:
        logger.info(f"Converting speech to text from {audio.filename}")
        # TODO: Implement Whisper.cpp STT
        return {
            "status": "success",
            "text": "Transcribed text here"
        }
    except Exception as e:
        logger.error(f"Error in STT: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting DRAVIS backend on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level=API_LOG_LEVEL
    )
