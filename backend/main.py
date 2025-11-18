"""DRAVIS FastAPI Backend - Complete Implementation"""
import os
import logging
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.config import Config
from backend.models.llm_manager import LLMManager
from backend.models.embedding_manager import EmbeddingManager
from backend.rag.document_parser import parse_document, chunk_text_for_storage
from backend.db.chroma_store import ChromaStore
from backend.db.sqlite_manager import SQLiteManager
from backend.speech.whisper_handler import transcribe_audio
from backend.quiz.quiz_generator import QuizGenerator
from backend.utils.language_detector import detect_language, should_respond_in_language
from backend.utils.pin_manager import save_pin_hash, verify_pin, pin_exists

# Ensure directories exist
Config.ensure_directories()

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title=Config.API_TITLE, version=Config.API_VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm = LLMManager()  # Uses Ollama if available, falls back to local llama-cpp
embedding_manager = EmbeddingManager()
chroma_store = ChromaStore(persist_directory=Config.CHROMA_PATH)
db_manager = SQLiteManager(db_path=Config.DB_PATH)
quiz_generator = QuizGenerator(llm_handler=llm)


# Request Models
class ChatRequest(BaseModel):
    message: str
    use_documents: bool = False
    mode: str = "normal"  # normal, exam_prep, practice, vocabulary
    conversation_id: Optional[str] = None


class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    quiz_type: str = "simple"  # simple or advanced
    use_documents: bool = False


class PINRequest(BaseModel):
    pin: str


class PINVerifyRequest(BaseModel):
    pin: str


# API Endpoints

@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "status": "Backend running",
        "llm_available": llm.is_available(),
        "version": Config.API_VERSION
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Chat endpoint with RAG support and multi-mode"""
    prompt = req.message.strip()
    
    if not prompt:
        return {"response": "Please enter a message.", "error": "empty_message"}
    
    # Detect language
    detected_lang, confidence = detect_language(prompt)
    logger.info(f"Detected language: {detected_lang} (confidence: {confidence})")
    
    # Build context based on mode
    context_parts = []
    
    # RAG: Retrieve relevant documents if enabled
    if req.use_documents:
        try:
            query_embedding = embedding_manager.embed(prompt)
            if query_embedding:
                results = chroma_store.query(query_embedding, top_k=Config.TOP_K_RESULTS)
                if results:
                    context_text = "\n\n".join([r["text"] for r in results[:3]])
                    context_parts.append(f"Relevant context from documents:\n{context_text}")
        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
    
    # Mode-specific prompts
    mode_prompts = {
        "normal": "",
        "exam_prep": "Provide a concise answer optimized for 10-minute rapid revision. Be brief and focused.",
        "practice": "After your answer, generate a follow-up practice question related to the topic.",
        "vocabulary": "Focus on word meanings, usage, and pronunciation. Explain vocabulary clearly."
    }
    
    mode_instruction = mode_prompts.get(req.mode, "")
    
    # Build final prompt
    full_prompt = prompt
    if context_parts:
        full_prompt = f"{prompt}\n\n{chr(10).join(context_parts)}"
    if mode_instruction:
        full_prompt = f"{mode_instruction}\n\n{full_prompt}"
    
    # Language-specific instruction
    if detected_lang == "hi" or (detected_lang == "hinglish" and confidence > 0.3):
        full_prompt = f"Respond in {detected_lang.upper()} if appropriate, or English if needed.\n\n{full_prompt}"
    
    # Generate response
    reply = llm.generate(full_prompt)
    
    if reply is None:
        # Fallback response when LLM is not available
        if not llm.is_available():
            return {
                "response": "I'm DRAVIS, your offline study assistant! The LLM model is not currently loaded. You can still:\n\n• Upload and manage documents\n• Generate quizzes\n• Use document search\n• Export chat history\n\nTo enable full chat responses, please download the Mistral 7B model file and place it in backend/models/",
                "error": "llm_not_available",
                "language": detected_lang,
                "mode": req.mode
            }
        return {"response": "LLM failed to generate a response.", "error": "generation_failed"}
    
    # Save to chat history
    try:
        db_manager.add_message(prompt, reply, use_rag=req.use_documents)
    except Exception as e:
        logger.error(f"Failed to save chat history: {e}")
    
    return {
        "response": reply,
        "language": detected_lang,
        "mode": req.mode
    }


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document"""
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{file_ext} not supported. Allowed: {Config.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > Config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {Config.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Save file
    file_path = os.path.join(Config.UPLOAD_DIR, f"{doc_id}_{file.filename}")
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    try:
        # Parse document
        pages = parse_document(file_path)
        
        # Chunk text
        chunks = chunk_text_for_storage(
            pages,
            chunk_size=Config.CHUNK_SIZE,
            overlap=Config.CHUNK_OVERLAP
        )
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text extracted from document")
        
        # Generate embeddings
        chunk_texts = [chunk[0] for chunk in chunks]
        embeddings = embedding_manager.embed_batch(chunk_texts)
        
        # Filter out None embeddings
        valid_chunks = []
        valid_embeddings = []
        for chunk, emb in zip(chunks, embeddings):
            if emb is not None:
                valid_chunks.append(chunk)
                valid_embeddings.append(emb)
        
        if not valid_chunks:
            raise HTTPException(status_code=500, detail="Failed to generate embeddings")
        
        # Store in ChromaDB
        chroma_store.add_document_chunks(
            document_id=doc_id,
            document_name=file.filename,
            chunks=valid_chunks,
            embeddings=valid_embeddings,
            upload_time=timestamp
        )
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "chunks": len(valid_chunks),
            "file_size": len(file_content),
            "upload_time": timestamp
        }
    
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        docs = chroma_store.get_document_info()
        return {"docs": docs, "count": len(docs)}
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        return {"docs": [], "count": 0}


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and all its chunks"""
    try:
        deleted_count = chroma_store.delete_document(document_id)
        
        # Also delete file from uploads
        upload_files = os.listdir(Config.UPLOAD_DIR)
        for filename in upload_files:
            if filename.startswith(document_id):
                file_path = os.path.join(Config.UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return {
            "success": True,
            "document_id": document_id,
            "chunks_deleted": deleted_count
        }
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@app.post("/api/stt")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """Speech-to-text using Whisper"""
    try:
        # Save uploaded audio temporarily
        temp_path = os.path.join(Config.UPLOAD_DIR, f"temp_{uuid.uuid4()}.wav")
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(audio_file.file, f)
        
        # Transcribe
        text, detected_lang = transcribe_audio(temp_path, language=language)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "text": text,
            "language": detected_lang,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"STT failed: {e}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")


@app.post("/api/quiz")
async def generate_quiz(req: QuizRequest):
    """Generate quiz questions"""
    try:
        # Get context from documents if requested
        context = None
        if req.use_documents:
            query_embedding = embedding_manager.embed(req.topic)
            if query_embedding:
                results = chroma_store.query(query_embedding, top_k=3)
                if results:
                    context = "\n\n".join([r["text"] for r in results])
        
        quiz = quiz_generator.generate_quiz(
            topic=req.topic,
            num_questions=req.num_questions,
            difficulty=req.difficulty,
            quiz_type=req.quiz_type,
            context=context
        )
        
        return {
            "success": True,
            "quiz": quiz,
            "topic": req.topic,
            "difficulty": req.difficulty,
            "type": req.quiz_type
        }
    
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@app.get("/api/chat/history")
async def get_chat_history(limit: int = 50):
    """Get chat history"""
    try:
        history = db_manager.get_history(limit=limit)
        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        return {"history": [], "count": 0}


@app.post("/api/chat/export")
async def export_chat_history():
    """Export chat history as Markdown"""
    try:
        history = db_manager.get_history(limit=1000)
        
        # Generate Markdown
        md_content = "# DRAVIS Chat History Export\n\n"
        md_content += f"Exported on: {datetime.now().isoformat()}\n\n"
        md_content += "---\n\n"
        
        for entry in reversed(history):  # Reverse to show oldest first
            md_content += f"## Conversation {entry['id']}\n\n"
            md_content += f"**Time:** {entry['time']}\n\n"
            md_content += f"**User:** {entry['user']}\n\n"
            md_content += f"**DRAVIS:** {entry['assistant']}\n\n"
            md_content += "---\n\n"
        
        # Save to file
        export_path = os.path.join(Config.DRAVIS_DATA_DIR, f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return FileResponse(
            export_path,
            media_type='text/markdown',
            filename=os.path.basename(export_path)
        )
    
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/api/pin/set")
async def set_pin(req: PINRequest):
    """Set 4-digit PIN"""
    try:
        if len(req.pin) != 4 or not req.pin.isdigit():
            raise HTTPException(status_code=400, detail="PIN must be exactly 4 digits")
        
        save_pin_hash(req.pin, Config.PIN_HASH_FILE)
        return {"success": True, "message": "PIN set successfully"}
    
    except Exception as e:
        logger.error(f"Failed to set PIN: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set PIN: {str(e)}")


@app.post("/api/pin/verify")
async def verify_pin_endpoint(req: PINVerifyRequest):
    """Verify PIN"""
    try:
        if len(req.pin) != 4 or not req.pin.isdigit():
            return {"verified": False, "error": "Invalid PIN format"}
        
        is_valid = verify_pin(req.pin, Config.PIN_HASH_FILE)
        return {"verified": is_valid}
    
    except Exception as e:
        logger.error(f"PIN verification failed: {e}")
        return {"verified": False, "error": str(e)}


@app.get("/api/pin/exists")
async def check_pin_exists():
    """Check if PIN is set"""
    exists = pin_exists(Config.PIN_HASH_FILE)
    return {"exists": exists}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting DRAVIS backend on {Config.HOST}:{Config.PORT}")
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
