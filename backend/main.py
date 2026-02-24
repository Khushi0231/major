"""DRAVIS FastAPI Backend - Complete Implementation"""
import os
import sys
import logging
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Correct imports based on actual folder structure
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
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
llm = LLMManager(Config.LLM_CONFIG)
embedding_manager = EmbeddingManager()
chroma_store = ChromaStore(persist_directory=Config.CHROMA_PATH)
db_manager = SQLiteManager(db_path=Config.DB_PATH)
quiz_generator = QuizGenerator(llm_handler=llm)


# Request Models
class ChatRequest(BaseModel):
    message: str
    use_documents: bool = False
    mode: str = "normal"
    conversation_id: Optional[str] = None


class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    quiz_type: str = "simple"
    use_documents: bool = False


class PINRequest(BaseModel):
    pin: str


class PINVerifyRequest(BaseModel):
    pin: str


@app.get("/")
def home():
    return {
        "status": "Backend running",
        "llm_available": llm.is_available(),
        "version": Config.API_VERSION
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    prompt = req.message.strip()

    if not prompt:
        return {"response": "Please enter a message.", "error": "empty_message"}

    detected_lang, confidence = detect_language(prompt)
    logger.info(f"Detected language: {detected_lang} (confidence: {confidence})")

    context_parts = []

    if req.use_documents:
        try:
            query_embedding = embedding_manager.embed(prompt)
            if query_embedding:
                results = chroma_store.query(query_embedding, top_k=Config.TOP_K_RESULTS)
                if results:
                    context_text = "\n\n".join([r["text"] for r in results[:3]])
                    context_parts.append(f"Relevant context:\n{context_text}")
        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")

    mode_prompts = {
        "normal": "",
        "exam_prep": "Provide a concise answer optimized for quick revision.",
        "practice": "After your answer, generate a practice question.",
        "vocabulary": "Explain vocabulary clearly with examples."
    }

    mode_instruction = mode_prompts.get(req.mode, "")

    full_prompt = prompt
    if context_parts:
        full_prompt = f"{prompt}\n\n{chr(10).join(context_parts)}"
    if mode_instruction:
        full_prompt = f"{mode_instruction}\n\n{full_prompt}"

    if detected_lang == "hi" or (detected_lang == "hinglish" and confidence > 0.3):
        full_prompt = f"Respond in {detected_lang.upper()} if appropriate.\n\n{full_prompt}"

    reply = llm.generate(full_prompt)

    if reply is None:
        msg = (
            "Model not loaded yet. Ensure Ollama is running, or GGUF model is inside backend/models."
        )
        return {
            "response": msg,
            "error": "llm_not_ready",
            "language": detected_lang,
            "mode": req.mode,
        }

    try:
        db_manager.add_message(prompt, reply, use_rag=req.use_documents)
    except Exception as e:
        logger.error(f"Failed to save chat history: {e}")

    return {"response": reply, "language": detected_lang, "mode": req.mode}


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f".{file_ext} not supported.")

    content = await file.read()
    if len(content) > Config.MAX_FILE_SIZE:
        raise HTTPException(400, "File too large.")

    doc_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    file_path = os.path.join(Config.UPLOAD_DIR, f"{doc_id}_{file.filename}")
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        pages = parse_document(file_path)
        chunks = chunk_text_for_storage(pages, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)

        if not chunks:
            raise HTTPException(400, "No text extracted.")

        texts = [c[0] for c in chunks]
        embeddings = embedding_manager.embed_batch(texts)

        valid_chunks = []
        valid_embeddings = []
        for chunk, emb in zip(chunks, embeddings):
            if emb is not None:
                valid_chunks.append(chunk)
                valid_embeddings.append(emb)

        if not valid_chunks:
            raise HTTPException(500, "Embedding generation failed.")

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
            "file_size": len(content),
            "upload_time": timestamp
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Processing failed: {str(e)}")


@app.post("/api/stt")
async def speech_to_text(audio_file: UploadFile = File(...), language: Optional[str] = Form(None)):
    try:
        temp_path = os.path.join(Config.UPLOAD_DIR, f"temp_{uuid.uuid4()}.wav")
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)

        text, detected_lang = transcribe_audio(temp_path, language=language)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {"text": text, "language": detected_lang, "success": True}

    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(500, f"Speech-to-text failed: {str(e)}")


@app.get("/api/documents")
async def list_documents():
    try:
        docs = chroma_store.get_document_info()
        formatted_docs = [
            {
                "document_id": doc["document_id"],
                "document_name": doc["document_name"],
                "upload_time": doc["upload_time"],
                "chunk_count": doc["chunk_count"]
            }
            for doc in docs
        ]
        return {"documents": formatted_docs}
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(500, "Failed to list documents")


@app.delete("/api/documents/{doc_name}")
async def delete_document(doc_name: str):
    try:
        # Get all documents to find the one with matching name
        all_docs = chroma_store.get_document_info()
        target_doc = None
        for doc in all_docs:
            if doc["document_name"] == doc_name or doc["document_id"] == doc_name:
                target_doc = doc
                break
        
        if not target_doc:
            raise HTTPException(404, f"Document {doc_name} not found")
        
        chroma_store.delete_document(target_doc["document_id"])
        return {"success": True, "message": f"Deleted {doc_name}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(500, "Failed to delete document")


@app.post("/api/quiz/generate")
async def generate_quiz_v2(req: QuizRequest):
    """Generate quiz from topic or documents"""
    try:
        context = None
        if req.use_documents:
            emb = embedding_manager.embed(req.topic)
            if emb:
                results = chroma_store.query(emb, top_k=3)
                if results:
                    context = "\n\n".join([r["text"] for r in results])

        quiz = quiz_generator.generate_quiz(
            topic=req.topic,
            num_questions=req.num_questions,
            difficulty=req.difficulty,
            quiz_type=req.quiz_type,
            context=context
        )

        return {"questions": quiz.get("questions", [])}

    except Exception as e:
        logger.error(f"Quiz error: {e}")
        raise HTTPException(500, "Quiz generation failed")


@app.get("/api/pin/exists")
async def check_pin_exists():
    return {"exists": pin_exists(Config.PIN_HASH_FILE)}


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend running",
        "version": Config.API_VERSION
    }

@app.post("/api/pin/verify")
async def verify_pin_route(req: PINVerifyRequest):
    if verify_pin(Config.PIN_HASH_FILE, req.pin):
        return {"verified": True}
    return {"verified": False, "error": "Invalid PIN"}

@app.post("/api/pin/set")
async def set_pin_route(req: PINRequest):
    if not req.pin or len(req.pin) != 4 or not req.pin.isdigit():
        return {"success": False, "error": "PIN must be exactly 4 digits"}

    try:
        save_pin_hash(req.pin, Config.PIN_HASH_FILE)
        return {"success": True, "verified": True, "message": "PIN saved successfully"}
    except Exception as e:
        logger.error(f"Error saving PIN: {e}")
        raise HTTPException(500, "Failed to save PIN")


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting DRAVIS backend on {Config.API_HOST}:{Config.API_PORT}")
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
