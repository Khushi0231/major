from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import uvicorn
import os

from backend.models.ollama_handler import OllamaHandler

llm = OllamaHandler()
from backend.rag.rag_store import add_document
from backend.rag.retriever import query_rag
from backend.rag.document_parser import extract_text_generic

app = FastAPI()
llm = OllamaHandler()

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = False
@app.post("/api/chat")
async def chat(payload: ChatRequest):
    user_msg = payload.message.strip()

    if not user_msg:
        return {"response": "Please enter a message.", "source": "system"}

    # 1. No RAG fallback for now until RAG functions are fixed
    prompt = user_msg

    # 2. Generate
    reply = llm.generate(prompt)

    if reply is None:
        return {"response": "LLM failed or offline", "source": "error"}

    return {"response": reply, "source": "llm"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    raw_text = extract_text_generic(await file.read())
    emb_model = llm.embedder
    embedding = emb_model.encode(raw_text)
    add_document(raw_text, embedding)
    return {"status": "Document added", "size": len(raw_text)}

@app.get("/")
def home():
    return {"status": "Backend running"}