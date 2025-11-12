
"""DRAVIS Backend - Main FastAPI Application"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
from datetime import datetime
from pathlib import Path

# Import modules
from backend.models.ollama_handler import OllamaHandler
from backend.models.embedding_manager import EmbeddingManager
from backend.rag.document_parser import DocumentParser
from backend.rag.retriever import Retriever
from backend.db.sqlite_manager import SQLiteManager
from backend.db.chroma_store import ChromaStore
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="DRAVIS Backend",
    description="Offline Claude-Style AI Study Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ollama = OllamaHandler()
em = EmbeddingManager(ollama)
retriever = Retriever(em)
db = SQLiteManager()
chroma = ChromaStore()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    use_rag: bool = False

class ChatResponse(BaseModel):
    response: str
    citations: List[dict]
    confidence: float

class UploadResponse(BaseModel):
    status: str
    filename: str
    size: int

# Endpoints
@app.get("/healthcheck")
async def healthcheck():
    """Service health check"""
    return {
        "status": "operational",
        "service": "DRAVIS Backend",
        "version": "1.0.0",
        "ollama_available": ollama.available,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process chat message with optional RAG"""
    try:
        logger.info(f"Chat: {request.message[:50]}...")
        
        # Generate response
        response_text = ollama.generate(request.message)
        
        # Get citations if RAG enabled
        citations = []
        if request.use_rag:
            results = retriever.retrieve(request.message, top_k=2)
            citations = [{"source": r["id"], "text": r["text"][:100]} for r in results]
        
        # Store in history
        db.add_message(request.message, response_text, request.use_rag)
        
        return ChatResponse(
            response=response_text,
            citations=citations,
            confidence=0.95
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and index document"""
    try:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = upload_dir / file.filename
        content = await file.read()
        
        with open(filepath, "wb") as f:
            f.write(content)
        
        # Parse document
        text = DocumentParser.parse(str(filepath))
        chunks = DocumentParser.chunk_text(text)
        
        # Add to retriever and chroma
        for i, chunk in enumerate(chunks):
            doc_id = f"{file.filename}_chunk_{i}"
            retriever.add_document(doc_id, chunk)
            embedding = em.embed(chunk)
            chroma.add(doc_id, chunk, embedding)
        
        logger.info(f"Uploaded: {file.filename}")
        
        return UploadResponse(
            status="success",
            filename=file.filename,
            size=len(content)
        )
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-docs")
async def list_documents():
    """List uploaded documents"""
    upload_dir = Path("data/uploads")
    docs = [f.name for f in upload_dir.glob("*")] if upload_dir.exists() else []
    return {"total": len(docs), "documents": docs}

@app.get("/chat-history")
async def chat_history(limit: int = 10):
    """Get chat history"""
    history = db.get_history(limit)
    return {"total": len(history), "history": history}

@app.post("/tts")
async def text_to_speech(text: str):
    """Text to speech (placeholder)"""
    logger.info(f"TTS: {text[:50]}...")
    return {"status": "success", "text": text, "audio_url": "/audio/output.wav"}

@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Speech to text (placeholder)"""
    logger.info(f"STT: {audio.filename}")
    return {"status": "success", "text": "[Transcribed from audio]"}

@app.get("/stats")
async def stats():
    """System statistics"""
    upload_dir = Path("data/uploads")
    num_docs = len(list(upload_dir.glob("*"))) if upload_dir.exists() else 0
    history = db.get_history(1)
    
    return {
        "documents_indexed": num_docs,
        "chat_messages": len(history),
        "retriever_docs": len(retriever.documents),
        "chroma_vectors": len(chroma.vectors)
    }

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         DRAVIS - Offline AI Study Assistant                  ║
    ║  Dynamic Reasoning AI for Virtual Intelligent Study          ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🚀 Starting DRAVIS Backend Server...
    📍 API: http://0.0.0.0:8000
    📚 Docs: http://localhost:8000/docs
    
    Endpoints:
    ✓ GET  /healthcheck      - Service status
    ✓ POST /chat             - Chat with AI
    ✓ POST /upload           - Upload documents
    ✓ GET  /list-docs        - List documents
    ✓ GET  /chat-history     - Get history
    ✓ POST /tts              - Text to speech
    ✓ POST /stt              - Speech to text
    ✓ GET  /stats            - System stats
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
