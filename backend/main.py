from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from models.ollama_handler import OllamaHandler

app = FastAPI()

# CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = OllamaHandler()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "Backend running", "llm_available": llm.is_available()}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    prompt = req.message.strip()

    if not prompt:
        return {"response": "Please enter a message."}

    reply = llm.generate(prompt)

    if reply is None:
        return {"response": "LLM failed to generate a response."}

    return {"response": reply}
