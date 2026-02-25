import os
import sys
import multiprocessing
import uvicorn
import logging
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DRAVIS-Bridge")

def run_auth():
    from auth.app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

def run_chat():
    from chat.app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="error")

def run_document():
    from document.app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8003, log_level="error")

def run_quiz():
    from quiz.app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8004, log_level="error")

def run_speech():
    try:
        from speech.app.main import app
        uvicorn.run(app, host="127.0.0.1", port=8005, log_level="error")
    except Exception as e:
        logger.error(f"Speech service failed to start: {e}")

def run_gateway():
    """Simple FastAPI gateway to replace Nginx in desktop mode."""
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse
    import httpx
    
    app = FastAPI(title="DRAVIS Desktop Gateway")
    client = httpx.AsyncClient()

    SERVICE_MAP = {
        "auth": "http://127.0.0.1:8001",
        "chat": "http://127.0.0.1:8002",
        "documents": "http://127.0.0.1:8003",
        "quiz": "http://127.0.0.1:8004",
        "speech": "http://127.0.0.1:8005",
    }

    @app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def proxy(service: str, path: str, request: Request):
        if service not in SERVICE_MAP:
            return {"error": "Service not found"}, 404
            
        url = f"{SERVICE_MAP[service]}/{path}"
        req = client.build_request(
            method=request.method,
            url=url,
            headers=request.headers.raw,
            content=await request.body(),
            params=request.query_params
        )
        res = await client.send(req, stream=True)
        return StreamingResponse(
            res.aiter_raw(),
            status_code=res.status_code,
            headers=res.headers
        )

    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="error")

if __name__ == "__main__":
    # On Windows, you must call freeze_support() if you use multiprocessing
    multiprocessing.freeze_support()
    
    logger.info("Initializing DRAVIS Native Services...")
    
    # Ensure local data directories exist
    os.makedirs("./uploads", exist_ok=True)
    os.makedirs("./chroma_db", exist_ok=True)
    
    processes = [
        multiprocessing.Process(target=run_auth, name="Auth-Svc"),
        multiprocessing.Process(target=run_chat, name="Chat-Svc"),
        multiprocessing.Process(target=run_document, name="Doc-Svc"),
        multiprocessing.Process(target=run_quiz, name="Quiz-Svc"),
        multiprocessing.Process(target=run_speech, name="Speech-Svc"),
        multiprocessing.Process(target=run_gateway, name="Gateway-Svc"),
    ]
    
    for p in processes:
        p.start()
        logger.info(f"Started {p.name} (PID: {p.pid})")
        
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        logger.info("Shutting down services...")
        for p in processes:
            p.terminate()
