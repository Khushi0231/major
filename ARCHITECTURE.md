# DRAVIS Enterprise Architecture

> **D**ynamic **R**easoning **A**I for **V**irtual **I**ntelligent **S**tudy

## System Overview

DRAVIS is built as a **microservices architecture** with 5 independent services, orchestrated via Docker Compose locally and Kubernetes for production.

```
 ┌──────────────────────────────────────────────────────────┐
 │                    Nginx Gateway (:80)                    │
 │         Frontend SPA + Reverse Proxy + Load Balancer     │
 └─────┬────────┬────────┬────────┬────────┬───────────────┘
       │        │        │        │        │
       ▼        ▼        ▼        ▼        ▼
   ┌──────┐ ┌──────┐ ┌────────┐ ┌──────┐ ┌────────┐
   │ Auth │ │ Chat │ │  Doc   │ │ Quiz │ │ Speech │
   │:8001 │ │:8002 │ │ :8003  │ │:8004 │ │ :8005  │
   └──┬───┘ └──┬───┘ └──┬──┬──┘ └──┬───┘ └────────┘
      │        │        │  │       │
      ▼        ▼        ▼  ▼       │  (inter-service)
   ┌──────────────┐  ┌────────┐   │
   │  MySQL 8.0   │  │ChromaDB│   ├──→ Chat  /generate
   │  (port 3306) │  │(:8010) │   └──→ Doc   /query
   └──────────────┘  └────────┘
```

## Services

| Service | Port | Responsibilities | Database |
|---------|------|------------------|----------|
| **Gateway** | 80 (ext: 8080) | Nginx reverse proxy, frontend SPA, routing | – |
| **Auth** | 8001 | PIN set/verify/exists, authentication | MySQL |
| **Chat** | 8002 | LLM interaction (Ollama/OpenAI), chat history, RAG queries | MySQL |
| **Document** | 8003 | File upload, parsing (PDF/DOCX/PPTX/TXT/images), embedding, vector search | MySQL + ChromaDB |
| **Quiz** | 8004 | Quiz generation via Chat + Document services | – (stateless) |
| **Speech** | 8005 | Audio transcription via Whisper | – (optional profile) |

## LLM Fallback Chain

```
Ollama (local, free)  →  OpenAI (cloud, paid)  →  Mock (always-on)
```

The system prioritises **offline-first** with local Ollama, automatically falls back to OpenAI if an API key is set, and uses a Mock provider as a safety net for testing.

## API Routes (via Gateway)

```
/api/health                  → Gateway health
/api/auth/pin/set            → Set 4-digit PIN
/api/auth/pin/verify         → Verify PIN
/api/auth/pin/exists         → Check if PIN is configured
/api/chat/send               → Send chat message
/api/chat/generate           → Internal LLM generation (for Quiz)
/api/chat/history             → Get chat history
/api/chat/export             → Export chat as markdown
/api/documents/upload        → Upload document
/api/documents/list          → List all documents
/api/documents/{id}          → Delete document
/api/documents/query         → Semantic search
/api/quiz/generate           → Generate quiz
/api/speech/transcribe       → Audio → text
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript + Vite |
| Gateway | Nginx 1.25 |
| Services | Python 3.11, FastAPI, Uvicorn |
| Relational DB | MySQL 8.0 |
| Vector DB | ChromaDB 0.4.22 |
| Embeddings | sentence-transformers (MiniLM-L6-v2) |
| LLM (local) | Ollama (llama3.1:8b) |
| LLM (cloud) | OpenAI GPT-3.5-turbo |
| STT | OpenAI Whisper |
| Orchestration | Docker Compose (local), Kubernetes (prod) |

## Quick Start

### Docker Compose (recommended)
```bash
# Start all services
docker-compose up --build -d

# Include Speech (heavy, optional)
docker-compose --profile full up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```
Access at **http://localhost:8080**

### Kubernetes
```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/mysql.yml
kubectl apply -f k8s/chromadb.yml
kubectl apply -f k8s/services.yml
```
Access at **http://localhost:30080**

### Development (no Docker)
```bash
# Terminal 1: Frontend
cd frontend && npm install && npm run dev

# Terminal 2-6: Each service
cd services/auth && pip install -r requirements.txt && uvicorn app.main:app --port 8001
cd services/chat && pip install -r requirements.txt && uvicorn app.main:app --port 8002
cd services/document && pip install -r requirements.txt && uvicorn app.main:app --port 8003
cd services/quiz && pip install -r requirements.txt && uvicorn app.main:app --port 8004
cd services/speech && pip install -r requirements.txt && uvicorn app.main:app --port 8005
```

## Project Structure

```
major/
├── docker-compose.yml         # Local orchestration
├── init.sql                   # MySQL schema
├── .env                       # Environment variables
├── START.bat                  # Windows launcher
├── ARCHITECTURE.md            # This file
│
├── frontend/                  # React SPA
│   └── src/
│       ├── App.tsx
│       ├── components/        # ChatPanel, DocumentsPanel, QuizPanel, etc.
│       └── utils/api.ts       # API client (all routes go via gateway)
│
├── services/
│   ├── gateway/               # Nginx + built frontend
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   ├── auth/                  # PIN authentication
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   ├── chat/                  # LLM interaction + history
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       └── llm/           # Provider framework
│   │           └── providers/ # Ollama, OpenAI, Mock
│   ├── document/              # Upload, parse, embed, search
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   ├── quiz/                  # Quiz generation (stateless)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   └── speech/                # Whisper STT (optional)
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app/
│
├── k8s/                       # Kubernetes manifests
│   ├── namespace.yml
│   ├── mysql.yml
│   ├── chromadb.yml
│   └── services.yml
│
└── backend/                   # Original monolith (preserved for reference)
```

## Key Design Decisions

1. **Sync LLM calls** — All LLM providers use synchronous Python (no `async`). This avoids the `loop.run_until_complete` deadlock that existed in the original monolith.

2. **Inter-service HTTP** — Quiz calls Chat's `/generate` endpoint for LLM access, and Document's `/query` for RAG context. No shared libraries or imports between services.

3. **Single database, separate tables** — All services share one MySQL instance but own distinct tables (`auth_pins`, `chat_messages`, `documents`). This simplifies local setup while maintaining logical separation.

4. **ChromaDB server mode** — ChromaDB runs as a standalone container accessed via HTTP, not embedded in the Document service. This allows independent scaling and persistence.

5. **Gateway-first routing** — All frontend requests go through Nginx, which handles path-based routing to services. No CORS issues, no hardcoded ports in the frontend.

6. **Optional Speech** — The Speech service is behind a Docker Compose profile (`full`) because Whisper model downloads are heavy. Core functionality works without it.
