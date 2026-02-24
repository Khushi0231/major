# DRAVIS — Enterprise Containerisation Roadmap
*Last updated: 2026-02-24 | Status: Pre-implementation planning*

---

## 1. Current State of the Project

### ✅ What Is Working Today (locally)

| Layer | Status | Notes |
|-------|--------|-------|
| React + Vite Frontend | ✅ Running | Port 5173 — all panels styled correctly |
| FastAPI Backend | ✅ Running | Port 8000 — all API routes respond |
| Backend ↔ Frontend Connectivity | ✅ Fixed | Green status indicator confirmed |
| Chat API (`/api/chat`) | ✅ Working | Mock provider active (returns deterministic test responses) |
| Documents API (`/api/upload`, `/api/documents`, DELETE) | ✅ Working | File parsing + ChromaDB embeddings functional |
| Quiz API (`/api/quiz/generate`) | ✅ Working | Returns fallback quiz when no LLM |
| PIN Lock (`/api/pin/set`, `/api/pin/verify`, `/api/pin/exists`) | ✅ Fixed | Argument order bug was fixed |
| Vector Store | ✅ Working | ChromaDB embedded, persisted to `chroma_db/` |
| Embeddings | ✅ Working | `sentence-transformers/all-MiniLM-L6-v2` running on MPS (Mac GPU) |
| SQLite history | ✅ Working | `dravis_data/dravis.db` |
| GGUF Provider (llama-cpp-python) | ⚠️ Broken | Model file is truncated (70 MB instead of ~4.37 GB) |
| Ollama Provider | ❌ Not active | Ollama not installed on this machine |
| Real AI Responses (Mistral 7B) | ❌ Not working | Depends on above two items |
| Docker / Containerisation | ❌ Stub only | Existing `Dockerfile` uses wrong CMD (`flask run` on a FastAPI app) |
| Kubernetes | ❌ Not started | No k8s manifests exist yet |
| GitHub push | ❌ Not done | Local only — no remote repo connected |

### ⚠️ Known Issues in Existing Files

| File | Problem |
|------|---------|
| `Dockerfile` | Uses `CMD ["flask", "run"]` — this is a FastAPI/uvicorn app, not Flask |
| `docker-compose.yml` | Only defines the backend container, no Ollama sidecar, no frontend service |
| `frontend/src/App.tsx` | Health check hardcoded to `http://localhost:8000` — breaks inside Docker |
| `frontend/src/utils/api.ts` | API base hardcoded to `http://localhost:8000/api` — breaks in Docker/Codespaces |
| `backend/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf` | File is only 70 MB (truncated). Actual size must be ~4.37 GB |
| Multiple stale `.md` docs | 10+ docs from previous sessions — will be archived |

---

## 2. End Goal (What We Are Building)

```
┌─────────────────────────────────────────────────────────────────┐
│                  DRAVIS — Containerised Stack                   │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │   Frontend   │   │   Backend    │   │      Ollama        │  │
│  │  (React/Vite)│──▶│  (FastAPI)   │──▶│  Mistral 7B Model  │  │
│  │  nginx:80    │   │  uvicorn:8000│   │  Port 11434        │  │
│  └──────────────┘   └──────────────┘   └────────────────────┘  │
│          │                  │                                   │
│          │            ┌─────┴──────┐                            │
│          │            │  ChromaDB  │  (vector store)            │
│          │            │  SQLite    │  (chat history, PIN)       │
│          │            └────────────┘                            │
│                                                                 │
│  All running via:  docker-compose up                            │
│  Anyone downloads the repo + runs one command → fully offline   │
└─────────────────────────────────────────────────────────────────┘
```

**Core requirements:**
1. **One command to start**: `docker-compose up` brings everything up
2. **Fully offline after first pull**: No internet needed at runtime
3. **Mistral 7B quality**: Full model, not a mini/quantized compromise
4. **Works on GitHub Codespaces**: For team collaboration
5. **Pushable to GitHub**: Repo size stays within GitHub limits (~500 MB soft limit, 2 GB hard limit)

---

## 3. The Model Distribution Problem — All Options

This is the central challenge. Mistral 7B Q4_K_M = **~4.37 GB**. GitHub's file limit is **100 MB** per file, and LFS has a **1 GB free quota per repo**.

### Option A — Ollama pulls the model at container start ✅ RECOMMENDED
- The `ollama` Docker image automatically pulls `mistral` on first run
- Model is stored in a Docker volume (`ollama_data`) and **cached forever**
- Subsequent `docker-compose up` = instant start (no re-download)
- **Repo size**: Not affected at all (model never enters git)
- **First run**: Requires ~4.5 GB download (one time only)
- **Offline after first run**: Yes — volume persists across restarts

```yaml
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama          # official image, includes model manager
    volumes:
      - ollama_data:/root/.ollama  # model cached here forever
    environment:
      - OLLAMA_MODELS=mistral      # auto-pulls on start
```

### Option B — GitHub Releases attachment
- Compress the `.gguf` to `.tar.gz` (~68 MB savings — negligible)
- Attach as a GitHub Release asset (no git size limits for releases)
- Startup script `wget`s the model from the release URL
- **Problem**: Still ~4.37 GB download every fresh `docker build`; slow; fragile

### Option C — Git LFS
- Store `.gguf` in Git LFS
- **Problem**: LFS free quota is 1 GB/month bandwidth. A 4.37 GB model blows this on first clone

### Option D — Hugging Face Hub download at startup
- Pull from `TheBloke/Mistral-7B-Instruct-v0.2-GGUF` via `huggingface_hub` Python package
- Cache in a Docker volume
- **Problem**: Bypasses Ollama's model management, needs `llama-cpp-python` compiled from source

### Decision: **Option A (Ollama Docker sidecar)** is the right choice because:
- Zero repo size impact
- Official `ollama/ollama` image handles everything
- Model cache is persistent across restarts
- Any teammate just runs `docker-compose up` — Ollama pulls once, done

---

## 4. Proposed Docker Architecture

### Services in `docker-compose.yml`

```
frontend   → nginx, serves built React app, proxies /api/* to backend
backend    → uvicorn FastAPI, talks to ollama + chromadb volume
ollama     → official ollama/ollama image, serves mistral at :11434
```

No separate ChromaDB container needed — embedded ChromaDB (already working) is good enough for V1. We keep SQLite too for simplicity.

### Why NOT full microservices for now
The user requested "make it respond first, other features can be added anytime." Splitting into 6 microservices (Auth, Chat, Document, Quiz, Speech, Gateway) adds significant complexity and is not needed to achieve the end goal. We will use **monolith-in-a-container** for V1 with the door open to split later.

---

## 5. Tech Stack Changes Required

| Component | Current | New | Reason |
|-----------|---------|-----|--------|
| LLM Runtime | `llama-cpp-python` (broken GGUF) | `ollama/ollama` Docker image | Official, stable, cached, Mistral 7B |
| Frontend serving | Vite dev server | nginx (production build) | Docker-appropriate |
| API URL in frontend | `http://localhost:8000` (hardcoded) | Environment variable via Vite | Works in any environment |
| Health check URL | `http://localhost:8000` (hardcoded) | Dynamic from env | Works in Docker |
| Docker CMD | `flask run` (wrong!) | `uvicorn backend.main:app` | Correct runtime |
| docker-compose | Backend only (stub) | Full stack: frontend + backend + ollama | Complete |

---

## 6. Implementation Plan (Phases)

### Phase 1 — Make AI Respond (Priority #1)
*Goal: Real Mistral 7B responses via Ollama*

- [ ] Fix `OllamaProvider` to handle the model being warm (Ollama takes 30s to load on first query)
- [ ] Add Ollama health/readiness wait logic to backend startup
- [ ] Write correct `docker-compose.yml` with Ollama sidecar
- [ ] Write correct `Dockerfile` for backend (fix the `flask run` bug)
- [ ] Write `Dockerfile.frontend` for nginx-served frontend
- [ ] Fix the hardcoded API URLs in frontend to use Vite env vars (`VITE_API_URL`)
- [ ] Create `nginx.conf` to proxy `/api/*` → backend and serve React app

### Phase 2 — Containerisation Polish
*Goal: `docker-compose up` works perfectly for anyone*

- [ ] Add `docker-compose.override.yml` for local dev (hot reload)
- [ ] Add health checks to all services
- [ ] Add restart policies
- [ ] Write `.dockerignore` to keep images small
- [ ] Create `init_ollama.sh` that waits for Ollama + pulls model if missing
- [ ] Add `START.bat` for Windows users (already has a stub)
- [ ] Test full cold-start on a clean machine

### Phase 3 — GitHub Codespaces
*Goal: Teammates open repo → click "Open in Codespace" → everything works*

- [ ] Update `.devcontainer/devcontainer.json` to use Docker Compose
- [ ] Forward ports 80, 8000, 11434
- [ ] Add `postStartCommand` to pull Mistral model via Ollama

### Phase 4 — Kubernetes (future)
- [ ] Namespace, Deployments, Services, PVC for ollama_data
- [ ] Ingress for external access
- [ ] HPA for backend scaling

---

## 7. Files to Create / Modify

| File | Action | Description |
|------|--------|-------------|
| `docker-compose.yml` | **Rewrite** | Full stack: frontend + backend + ollama |
| `Dockerfile` | **Rewrite** | Correct uvicorn CMD, proper layering |
| `Dockerfile.frontend` | **Create** | nginx serving built React + proxy config |
| `nginx.conf` | **Create** | Proxy /api/* to backend, serve React |
| `frontend/src/utils/api.ts` | **Fix** | Use `VITE_API_URL` env var |
| `frontend/src/App.tsx` | **Fix** | Health check uses env var |
| `.env.example` | **Update** | Add `VITE_API_URL`, `OLLAMA_MODEL` |
| `.dockerignore` | **Create** | Exclude `.venv`, `node_modules`, `.gguf` |
| `backend/models/providers/ollama_provider.py` | **Improve** | Add retry logic for model warmup |
| `scripts/init_ollama.sh` | **Create** | Wait for Ollama + auto-pull Mistral |
| `backend/models/mistral*.gguf` | **Delete** | Truncated/broken file — Ollama replaces it |
| **10 stale `.md` docs** | **Archive** | Move to `docs/archive/` |
| `k8s/` | **Create (Phase 4)** | Kubernetes manifests |

---

## 8. Open Questions (Need Your Answers Before Coding)

1. **Ollama model name**: Should we use `mistral` (7B, ~4 GB) or `mistral:7b-instruct` (instruct-tuned, better for Q&A)? The instruct variant is better for your study assistant use case.

2. **GPU in Docker**: Do you or your teammates have NVIDIA GPUs? If yes, we can pass `--gpus all` in compose for 10x faster inference. If Mac-only (Apple Silicon), we use CPU mode in Docker (Metal is not available inside Docker containers on Mac).

3. **Frontend serving in production**: Should the React app be served by:
   - **nginx inside Docker** (recommended — clean, production-grade), or  
   - **Vite dev server** (easier but not for production)?

4. **Database**: Keep SQLite (simple, zero setup) or switch to MySQL/PostgreSQL (more enterprise, needed for multi-instance scaling)? For V1 (single container), SQLite is perfectly fine.

5. **GitHub repo**: Do you already have a GitHub remote set up for this project, or do we need to initialise a new repo and push for the first time?

6. **Git branch name**: What should the feature branch be called? Suggestion: `feature/docker-containerisation`

7. **Windows support**: Should `START.bat` launch Docker Compose, or should it also try to run without Docker (native Python/Node)?

---

## 9. What Will NOT Change

- Frontend component code (Chat, Docs, Quiz, Settings, PINLock, VoiceControls) — already fixed and working
- Backend API routes and logic in `main.py`
- ChromaDB embedded store (no separate container needed for V1)
- SQLite for chat history and PIN storage
- The `sentence-transformers` embedding pipeline

---

## 10. Summary

**To answer your core question: How do we attach Mistral 7B to DRAVIS without increasing repo size?**

**Answer: We don't store the model in the repo at all. We use the official `ollama/ollama` Docker image as a sidecar service. It pulls and caches Mistral 7B in a Docker named volume (`ollama_data`) on first `docker-compose up`. Every subsequent start is instant. The repo stays small. Anyone with Docker installed runs one command and gets the full 7B model offline.**

---

*Please answer the 7 questions in Section 8, then implementation begins immediately on a new git branch.*
