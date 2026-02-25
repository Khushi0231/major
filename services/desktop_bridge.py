"""DRAVIS Desktop Bridge — Unified backend for native desktop app.

Runs all microservices (Auth, Chat, Document, Quiz) as threads in one process,
plus a lightweight FastAPI gateway on port 8080.
Manages Ollama lifecycle: starts it, pulls model on first run, stops on exit.
"""
import os
import sys
import time
import signal
import shutil
import logging
import subprocess
import threading
from pathlib import Path

import uvicorn

# Add the services root to path
SERVICES_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SERVICES_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger("DRAVIS-Bridge")

# ─── Data directories ─────────────────────────────
APP_DATA = os.path.join(os.path.expanduser("~"), ".dravis")
os.makedirs(APP_DATA, exist_ok=True)
os.makedirs(os.path.join(APP_DATA, "uploads"), exist_ok=True)
os.makedirs(os.path.join(APP_DATA, "chroma_db"), exist_ok=True)

# Set environment variables for all services (desktop mode)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(APP_DATA, 'dravis.db')}")
os.environ.setdefault("CHROMADB_PERSIST_DIR", os.path.join(APP_DATA, "chroma_db"))
os.environ.setdefault("UPLOAD_DIR", os.path.join(APP_DATA, "uploads"))
os.environ.setdefault("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
os.environ.setdefault("OLLAMA_MODEL", "llama3.2:3b")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Remove CHROMADB_HOST so document service uses local persistence
os.environ.pop("CHROMADB_HOST", None)


# ─── Ollama Management ────────────────────────────

_ollama_process = None
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


def _find_ollama() -> str | None:
    """Find the Ollama binary on the system."""
    return shutil.which("ollama")


def _is_ollama_running() -> bool:
    """Check if Ollama server is already running."""
    import requests
    try:
        resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def _start_ollama():
    """Start Ollama server if not already running."""
    global _ollama_process

    if _is_ollama_running():
        logger.info("Ollama is already running")
        return True

    ollama_path = _find_ollama()
    if not ollama_path:
        logger.error(
            "Ollama not found! Please install Ollama from https://ollama.com "
            "DRAVIS needs Ollama for AI capabilities."
        )
        return False

    logger.info(f"Starting Ollama server ({ollama_path})...")
    _ollama_process = subprocess.Popen(
        [ollama_path, "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for Ollama to be ready
    for i in range(30):
        if _is_ollama_running():
            logger.info("Ollama server is ready")
            return True
        time.sleep(1)

    logger.error("Ollama failed to start within 30 seconds")
    return False


def _ensure_model():
    """Pull the model if it's not already downloaded."""
    import requests
    try:
        resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            # Check if our model (or a variant) is present
            if any(OLLAMA_MODEL in m for m in models):
                logger.info(f"Model '{OLLAMA_MODEL}' is already downloaded")
                return True
    except Exception:
        pass

    logger.info(f"Downloading model '{OLLAMA_MODEL}'... (this may take several minutes on first run)")
    ollama_path = _find_ollama()
    if not ollama_path:
        return False

    try:
        result = subprocess.run(
            [ollama_path, "pull", OLLAMA_MODEL],
            capture_output=True,
            text=True,
            timeout=600,  # 10 min timeout for model download
        )
        if result.returncode == 0:
            logger.info(f"Model '{OLLAMA_MODEL}' downloaded successfully")
            return True
        else:
            logger.error(f"Model pull failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("Model download timed out (10 minutes)")
        return False


def _stop_ollama():
    """Stop the Ollama server if we started it."""
    global _ollama_process
    if _ollama_process:
        logger.info("Stopping Ollama server...")
        _ollama_process.terminate()
        _ollama_process.wait(timeout=5)
        _ollama_process = None


# ─── Service Runners ──────────────────────────────

def _run_service(name: str, module_path: str, port: int):
    """Run a FastAPI service as a uvicorn server."""
    os.environ["SERVICE_NAME"] = name
    os.environ["SERVICE_PORT"] = str(port)
    try:
        uvicorn.run(module_path, host="127.0.0.1", port=port, log_level="warning")
    except Exception as e:
        logger.error(f"{name} service failed: {e}")


def _run_gateway():
    """Simple reverse-proxy gateway that routes /api/{service}/* to the right port."""
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    import httpx

    app = FastAPI(title="DRAVIS Desktop Gateway")
    client = httpx.AsyncClient(timeout=120)

    SERVICE_MAP = {
        "auth": "http://127.0.0.1:8001",
        "chat": "http://127.0.0.1:8002",
        "documents": "http://127.0.0.1:8003",
        "quiz": "http://127.0.0.1:8004",
        "speech": "http://127.0.0.1:8005",
    }

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "service": "gateway", "mode": "desktop"}

    @app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def proxy(service: str, path: str, request: Request):
        if service not in SERVICE_MAP:
            return JSONResponse({"error": f"Unknown service: {service}"}, 404)

        url = f"{SERVICE_MAP[service]}/{path}"
        try:
            req = client.build_request(
                method=request.method,
                url=url,
                headers={
                    k.decode(): v.decode()
                    for k, v in request.headers.raw
                    if k.decode().lower() not in ("host", "transfer-encoding")
                },
                content=await request.body(),
                params=request.query_params,
            )
            resp = await client.send(req, stream=True)
            return StreamingResponse(
                resp.aiter_raw(),
                status_code=resp.status_code,
                headers=dict(resp.headers),
            )
        except httpx.ConnectError:
            return JSONResponse({"error": f"Service '{service}' not ready"}, 503)

    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="warning")


# ─── Main ─────────────────────────────────────────

def main():
    logger.info("=" * 50)
    logger.info("  DRAVIS Desktop — Starting up...")
    logger.info(f"  Data directory: {APP_DATA}")
    logger.info("=" * 50)

    # 1. Start Ollama
    ollama_ok = _start_ollama()
    if ollama_ok:
        _ensure_model()
    else:
        logger.warning("Continuing without Ollama — AI features will be limited")

    # 2. Start services in threads
    services = [
        ("Auth",     "auth.app.main:app",     8001),
        ("Chat",     "chat.app.main:app",     8002),
        ("Document", "document.app.main:app", 8003),
        ("Quiz",     "quiz.app.main:app",     8004),
    ]

    threads = []
    for name, module, port in services:
        t = threading.Thread(
            target=_run_service,
            args=(name, module, port),
            name=f"{name}-Svc",
            daemon=True,
        )
        t.start()
        threads.append(t)
        logger.info(f"  Started {name} service on port {port}")

    # 3. Start gateway (blocks)
    logger.info("")
    logger.info("  DRAVIS is ready at http://127.0.0.1:8080")
    logger.info("  Press Ctrl+C to stop")
    logger.info("")

    try:
        _run_gateway()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Shutting down DRAVIS...")
        _stop_ollama()
        logger.info("Goodbye!")


if __name__ == "__main__":
    # Required for PyInstaller on Windows
    import multiprocessing
    multiprocessing.freeze_support()
    main()
