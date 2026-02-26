"""Chat Service - API Routes"""
import logging
from typing import Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, ChatMessage, ChatSetting, engine
from .schemas import (
    ChatRequest, ChatResponse,
    GenerateRequest, GenerateResponse,
    HistoryResponse, HistoryItem,
    HealthResponse,
)
from .llm import LLMManager
from .language_detector import detect_language

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── Initialise LLM Manager at module level ────
_llm = LLMManager({
    # PRIMARY: LangChain + Ollama with llama3.1:8b
    "ollama": {
        "base_url": settings.OLLAMA_BASE_URL,
        "model": settings.OLLAMA_MODEL,   # default: llama3.1:8b
        "timeout": settings.OLLAMA_TIMEOUT,
        "temperature": 0.6,
    },
    # SECONDARY: Mistral via raw Ollama API
    "mistral": {
        "base_url": settings.OLLAMA_BASE_URL,
        "model": "mistral",
        "timeout": settings.OLLAMA_TIMEOUT,
    },
    # CLOUD FALLBACKS
    "groq": {
        "api_key": settings.GROQ_API_KEY,
        "model": settings.GROQ_MODEL,
    },
    "openai": {
        "api_key": settings.OPENAI_API_KEY,
        "model": settings.OPENAI_MODEL,
        "temperature": settings.OPENAI_TEMPERATURE,
    },
})

MODE_PROMPTS = {
    "normal": "",
    "exam_prep": (
        "The user is preparing for an exam. Give a concise, well-structured answer "
        "using headings and bullet points. Include key definitions, formulas, or steps where relevant."
    ),
    "practice": (
        "First answer the user's question clearly. Then at the end, add a section "
        "titled 'Practice Question:' with one related question the user can try."
    ),
    "vocabulary": (
        "Focus on vocabulary and language. Define key terms clearly, give example sentences, "
        "and explain any nuance or common confusion."
    ),
}


# ─── Chat ───────────────────────────────────────

@router.post("/send", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Main chat endpoint — processes message with optional RAG context."""
    prompt = req.message.strip()
    if not prompt:
        return ChatResponse(response="Please enter a message.", error="empty_message")

    lang, confidence = detect_language(prompt)
    logger.info(f"Language: {lang} ({confidence:.2f})")

    # Gather RAG context from Document Service
    rag_context = ""
    if req.use_documents:
        try:
            resp = httpx.post(
                f"{settings.DOCUMENT_SERVICE_URL}/query",
                json={"query": prompt, "top_k": 4},
                timeout=15,
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    rag_context = "\n\n".join(
                        f"[Source {i+1}]: {r['text']}"
                        for i, r in enumerate(results[:4])
                    )
        except Exception as e:
            logger.warning(f"Document service unreachable: {e}")

    # ── Build prompt ──────────────────────────────
    parts: list[str] = []

    # Mode instruction
    mode_instruction = MODE_PROMPTS.get(req.mode, "")
    if mode_instruction:
        parts.append(f"[Instruction: {mode_instruction}]")

    # Language hint removed — system prompt enforces English by default

    # RAG context — with strong grounding instruction
    if rag_context:
        parts.append(
            "IMPORTANT: The user has uploaded documents. "
            "Answer the question ONLY based on the document content below. "
            "Do NOT answer from your general knowledge. "
            "Do NOT talk about yourself or DRAVIS. "
            "Quote or reference specific parts of the documents.\n\n"
            f"--- USER'S DOCUMENT CONTENT ---\n{rag_context}\n--- END OF DOCUMENT CONTENT ---"
        )

    # User question (always last)
    parts.append(f"User Question: {prompt}")

    full_prompt = "\n\n".join(parts)

    # Generate
    reply = _llm.generate(full_prompt)
    provider_name = _llm.get_active_provider() or "unknown"

    if reply is None:
        return ChatResponse(
            response="No LLM available. Ensure Ollama is running or set OPENAI_API_KEY.",
            error="llm_not_ready",
            language=lang,
            mode=req.mode,
        )

    # Persist to MySQL
    try:
        msg = ChatMessage(
            session_id=req.session_id or "default",
            user_message=prompt,
            assistant_response=reply,
            use_rag=req.use_documents,
            mode=req.mode,
            language=lang,
            provider=provider_name,
        )
        db.add(msg)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save chat: {e}")

    return ChatResponse(
        response=reply,
        language=lang,
        mode=req.mode,
        provider=provider_name,
    )


# ─── Internal Generate (for Quiz Service) ──────

@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Raw LLM generation — used internally by Quiz Service."""
    reply = _llm.generate(
        req.prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
    )
    if reply is None:
        raise HTTPException(503, "No LLM provider available")
    return GenerateResponse(
        response=reply,
        provider=_llm.get_active_provider() or "unknown",
    )


# ─── History ────────────────────────────────────

@router.get("/history", response_model=HistoryResponse)
def get_history(
    session_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(ChatMessage)
    if session_id:
        q = q.filter(ChatMessage.session_id == session_id)
    total = q.count()
    rows = q.order_by(ChatMessage.id.desc()).limit(limit).all()

    items = [
        HistoryItem(
            id=r.id,
            session_id=r.session_id,
            user_message=r.user_message,
            assistant_response=r.assistant_response,
            use_rag=r.use_rag or False,
            mode=r.mode or "normal",
            language=r.language,
            provider=r.provider,
            created_at=str(r.created_at),
        )
        for r in rows
    ]
    return HistoryResponse(messages=items, total=total)


# ─── Export ─────────────────────────────────────

@router.post("/export")
def export_history(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Export chat history as Markdown."""
    q = db.query(ChatMessage)
    if session_id:
        q = q.filter(ChatMessage.session_id == session_id)
    rows = q.order_by(ChatMessage.id.asc()).all()

    lines = ["# DRAVIS Chat Export\n"]
    for r in rows:
        lines.append(f"## You\n{r.user_message}\n")
        lines.append(f"## DRAVIS\n{r.assistant_response}\n")
        lines.append("---\n")

    md = "\n".join(lines)
    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=chat_export.md"},
    )


# ─── Health ─────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health_check():
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            from sqlalchemy import text as sa_text
            conn.execute(sa_text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        service="chat",
        database=db_status,
        llm_providers=_llm.health(),
    )
