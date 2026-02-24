# DRAVIS — Implementation Progress & Strategy

## 🎯 End Goal
> Anyone can download DRAVIS from the Vercel site, click "next-next-done" to install, and use it **fully offline** with **Mistral 7B quality** responses.

## 🧩 Core Problem
| Problem | Why It's Hard | Our Solution |
|---------|--------------|--------------|
| Mistral 7B is ~4.5 GB | Can't push to GitHub (100 MB limit) | **Ollama pulls it at first run** — model lives in Docker volume, not in repo |
| Ollama itself is ~500 MB | Same size issue | **Docker image pulls from Docker Hub** — `ollama/ollama:latest` is pulled by Docker Compose |
| Need offline after install | User may not have internet later | **First-run downloads everything**, then it's cached locally forever |
| "Next-next" install UX | Users aren't technical | **One-file installer** per OS that handles Docker + clone + model pull |

## ✅ What's Done

### Infrastructure
- [x] `docker-compose.yml` — 4 services: Ollama, model-init, backend, frontend
- [x] `Dockerfile.backend` — Python 3.11 slim, no apt-get (fast build)
- [x] `Dockerfile.frontend` — Node 20 build → nginx serve + API proxy
- [x] `nginx.conf` — reverse proxy: `/api/*` → backend, `/` → React SPA
- [x] `.dockerignore` — keeps images lean

### Backend (FastAPI)
- [x] `config.py` — env-based config, Ollama enabled by default
- [x] `llm_manager.py` — provider fallback: Ollama → GGUF → OpenAI → Mock
- [x] `ollama_provider.py` — HTTP calls to Ollama `/api/generate`
- [x] `embedding_manager.py` — sentence-transformers `all-MiniLM-L6-v2` for RAG
- [x] `chroma_store.py` — ChromaDB vector store for document embeddings
- [x] `document_parser.py` — PDF, DOCX, PPTX, TXT, images
- [x] `main.py` — chat, upload, quiz, PIN, health endpoints
- [x] `requirements.txt` — CPU-only PyTorch to reduce Docker image size

### Frontend (React + Vite)
- [x] Chat interface with mode selection
- [x] Document upload panel
- [x] Quiz generation
- [x] Voice input (Whisper)
- [x] PIN authentication
- [x] Health check indicator

### Installers
- [x] `installers/install-dravis-mac.command` — double-click on Mac
- [x] `installers/install-dravis-windows.ps1` — right-click Run with PowerShell
- [x] `installers/install-dravis-linux.sh` — `curl | bash` one-liner
- [x] `start.sh` / `START.bat` — for users who already have Docker

### Landing Page
- [x] `landing/index.html` — minimal dark theme, download buttons
- [x] Deployed to Vercel (dravis.vercel.app) — needs auth fix
- [x] `vercel.json` — static hosting config

### Git
- [x] `.gitignore` — ignores .gguf, .venv, chroma_db, dravis_data
- [x] `.gitattributes` — no LFS needed
- [x] Branch: `feature/docker-containerisation`
- [x] Pushed to `origin`

## ❌ What's NOT Done Yet

### Critical (Must Fix)
- [ ] **Verify Docker build completes** — pip install was slow on Mac Docker (ARM emulation), untested on Linux
- [ ] **Verify Ollama model pull works** in docker-compose — ollama-init service untested
- [ ] **Verify end-to-end chat** works through Docker (nginx → backend → Ollama → response)
- [ ] **Vercel deployment protection** — site requires login, needs to be public

### Nice to Have
- [ ] Kubernetes manifests (k8s/)
- [ ] GPU support profile in docker-compose
- [ ] Streaming responses
- [ ] Auto-update mechanism

## 🏗️ Architecture

```
User Browser (http://localhost)
     │
     ▼
┌─────────────────┐
│   nginx (:80)   │  ← serves React SPA + proxies API
└────────┬────────┘
         │ /api/*
         ▼
┌─────────────────┐
│ FastAPI (:8000)  │  ← chat, upload, quiz, PIN, health
│  sentence-trans  │  ← embeddings (all-MiniLM-L6-v2)
│  ChromaDB        │  ← vector store
│  SQLite          │  ← chat history, docs metadata
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│ Ollama (:11434) │  ← runs Mistral 7B locally
│  mistral model  │  ← cached in Docker volume (~4.5 GB)
└─────────────────┘
```

## 🔑 Distribution Architecture (No Large Files in Git)

```
GitHub Repo (~50 MB)     GitHub Container Registry     Ollama Registry
┌──────────────────┐    ┌──────────────────────┐    ┌────────────────┐
│ Source code       │    │ dravis-backend:latest │    │ mistral:latest │
│ docker-compose    │───▶│ dravis-frontend:latest│    │ (~4.5 GB)      │
│ GitHub Actions    │    │ (auto-built on push)  │    │ (pulled once)  │
│ Installer scripts │    └──────────────────────┘    └────────────────┘
└──────────────────┘              │                         │
                                  ▼                         ▼
                        User runs: docker compose up -d
                        Everything downloads automatically
```

## 📋 User Install Flow

```
1. Visit dravis.vercel.app → Click "Download for Mac/Win/Linux"
2. Double-click downloaded file
3. Script installs Docker (if needed)
4. Script downloads docker-compose.prod.yml (1 KB)
5. docker compose pull → pre-built images from ghcr.io (~1.5 GB)
6. docker compose up → Ollama pulls Mistral 7B (~4.5 GB, first run only)
7. Browser opens http://localhost → DRAVIS is ready
```

No git clone. No build step. No source code needed. Just Docker.

## ⚙️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + TypeScript + Vite | Fast, modern, typed |
| Backend | FastAPI + Python 3.11 | Async, fast, good ML ecosystem |
| LLM | Ollama + Mistral 7B | Offline, full quality, no API keys |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Lightweight, accurate for RAG |
| Vector DB | ChromaDB | Simple, no external server needed |
| Database | SQLite | Zero config, embedded |
| Proxy | nginx | Serves SPA + reverse proxy |
| Container | Docker Compose | One command orchestration |
| Hosting | Vercel (landing page only) | Free static hosting |

## 🔀 Git Branches
- `main` — stable, production
- `feature/docker-containerisation` — current work (DO NOT merge until tested)
