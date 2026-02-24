"""Quiz Service - API Routes

This service has NO LLM or DB of its own.
It calls Chat Service (/generate) for LLM and Document Service (/query) for RAG.
"""
import json
import logging
import httpx
from fastapi import APIRouter, HTTPException
from .config import settings
from .schemas import QuizRequest, QuizResponse, QuizQuestion, HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_simple_prompt(topic: str, n: int, diff: str, context: str = "") -> str:
    ctx = f"\n\nContext from documents:\n{context}" if context else ""
    return f"""Generate {n} {diff} difficulty quiz questions about: {topic}

Requirements:
- Mix of Multiple Choice (MCQ) and True/False questions
- MCQ: exactly 4 options (A, B, C, D)
- True/False: options A) True, B) False
- Provide correct answer letter
- Include 1-2 sentence explanation

Format as JSON:
{{"questions": [{{"type": "mcq", "question": "...", "options": ["A","B","C","D"], "correct_answer": "A", "explanation": "..."}}]}}
{ctx}
Return ONLY valid JSON, no extra text."""


def _build_advanced_prompt(topic: str, n: int, diff: str, context: str = "") -> str:
    ctx = f"\n\nContext from documents:\n{context}" if context else ""
    return f"""Generate {n} {diff} difficulty advanced quiz questions about: {topic}

Requirements:
- Mix of Fill-in-the-blank and Short Answer
- Fill-in-the-blank: use _____ for blanks
- Short Answer: 2-3 sentence answers
- Provide correct/sample answer and explanation

Format as JSON:
{{"questions": [{{"type": "fill_blank", "question": "...", "correct_answer": "...", "explanation": "..."}}]}}
{ctx}
Return ONLY valid JSON, no extra text."""


def _parse_quiz_json(text: str) -> list:
    """Extract JSON from LLM response (which may have markdown fences)."""
    # Strip markdown code fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start >= 0 and end > start:
        data = json.loads(cleaned[start:end])
        return data.get("questions", [])
    return []


def _fallback_quiz(topic: str, n: int, advanced: bool = False) -> list:
    """Generate placeholder quiz when LLM parsing fails."""
    qs = []
    for i in range(n):
        if advanced:
            qs.append(QuizQuestion(
                type="short_answer",
                question=f"Explain concept #{i+1} related to {topic}.",
                correct_answer=f"Sample answer for question {i+1}",
                explanation=f"This tests understanding of {topic}",
            ))
        else:
            qs.append(QuizQuestion(
                type="mcq",
                question=f"Question {i+1} about {topic}?",
                options=["Option A", "Option B", "Option C", "Option D"],
                correct_answer="A",
                explanation=f"Explanation for question {i+1}",
            ))
    return qs


# ─── Generate Quiz ──────────────────────────────

@router.post("/generate", response_model=QuizResponse)
def generate_quiz(req: QuizRequest):
    n = max(3, min(10, req.num_questions))

    # Get RAG context if requested
    context = ""
    if req.use_documents:
        try:
            resp = httpx.post(
                f"{settings.DOCUMENT_SERVICE_URL}/query",
                json={"query": req.topic, "top_k": 3},
                timeout=15,
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                context = "\n\n".join(r["text"] for r in results)
        except Exception as e:
            logger.warning(f"Document service unavailable: {e}")

    # Build prompt
    if req.quiz_type == "simple":
        prompt = _build_simple_prompt(req.topic, n, req.difficulty, context)
    else:
        prompt = _build_advanced_prompt(req.topic, n, req.difficulty, context)

    # Call Chat Service for LLM generation
    try:
        resp = httpx.post(
            f"{settings.CHAT_SERVICE_URL}/generate",
            json={"prompt": prompt, "max_tokens": 2000, "temperature": 0.7},
            timeout=120,
        )
        if resp.status_code != 200:
            logger.error(f"Chat service returned {resp.status_code}")
            return QuizResponse(questions=_fallback_quiz(req.topic, n, req.quiz_type != "simple"))

        llm_response = resp.json().get("response", "")

        # Parse JSON from LLM output
        raw_questions = _parse_quiz_json(llm_response)
        if raw_questions:
            questions = [
                QuizQuestion(
                    type=q.get("type", "mcq"),
                    question=q.get("question", ""),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", ""),
                    explanation=q.get("explanation", ""),
                )
                for q in raw_questions
            ]
            return QuizResponse(questions=questions)

    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")

    return QuizResponse(questions=_fallback_quiz(req.topic, n, req.quiz_type != "simple"))


# ─── Health ─────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health_check():
    chat_status = "unknown"
    doc_status = "unknown"
    try:
        r = httpx.get(f"{settings.CHAT_SERVICE_URL}/health", timeout=3)
        chat_status = "connected" if r.status_code == 200 else "disconnected"
    except Exception:
        chat_status = "disconnected"
    try:
        r = httpx.get(f"{settings.DOCUMENT_SERVICE_URL}/health", timeout=3)
        doc_status = "connected" if r.status_code == 200 else "disconnected"
    except Exception:
        doc_status = "disconnected"

    overall = "ok" if chat_status == "connected" else "degraded"
    return HealthResponse(
        status=overall, service="quiz",
        chat_service=chat_status, document_service=doc_status,
    )
