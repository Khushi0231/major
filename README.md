# DRAVIS 🎓
### Dynamic Reasoning AI for Virtual Intelligent Study

> 100% offline AI Study Assistant powered by **Mistral 7B Instruct** — zero cloud, zero data leaks, one command to start.

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://docker.com)
[![Ollama](https://img.shields.io/badge/Ollama-Mistral%207B-black?logo=ollama)](https://ollama.ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Mistral 7B Instruct** | Full 7B model via Ollama — not a mini version |
| 📚 **RAG from Your Docs** | Upload PDFs, DOCX, PPTs → AI answers from your material |
| 📝 **Quiz Generator** | MCQ, True/False, short-answer on any topic or document |
| 🗣️ **Speech-to-Text** | Whisper integration for hands-free interaction |
| 🌐 **Multilingual** | English, Hindi, Hinglish detection + response |
| 🔒 **PIN Lock** | Protect sessions with a local 4-digit PIN |
| ⚡ **NVIDIA GPU** | Auto-detected — 10x faster inference with CUDA |
| 🐋 **One Command** | `docker-compose up` starts everything |

---

## 🚀 Quick Start

### Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- ~6 GB free disk space (for Mistral 7B model — downloaded once, cached forever)
- 16 GB RAM recommended (8 GB minimum)

### Linux / macOS
```bash
git clone https://github.com/Khushi0231/major.git dravis
cd dravis
bash start.sh
```

### Windows
```
1. Install Docker Desktop
2. Clone this repo
3. Double-click START.bat
```

### With NVIDIA GPU (10x faster)
```bash
# Install NVIDIA Container Toolkit first:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
docker-compose up --build -d   # GPU auto-detected via docker-compose.yml
```

⏳ **First run**: Downloads Mistral 7B (~4.5 GB, one-time only)  
✅ **Subsequent starts**: Instant (model stays cached in Docker volume)

---

## 🌐 Access

| Service | URL |
|---------|-----|
| **DRAVIS App** | http://localhost |
| **Download Page** | http://localhost/download |
| **Backend API** | http://localhost/api |
| **API Docs** | http://localhost/api/docs |
| **Ollama** | http://localhost:11434 |

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │      nginx (port 80/8080)        │
                    │  Serves React · Proxies /api/*   │
                    └────────────┬────────────────────-┘
                                 │
              ┌──────────────────┴────────────────────┐
              │                                       │
   ┌──────────▼─────────┐              ┌──────────────▼──────────┐
   │   FastAPI Backend   │──────────▶  │    Ollama + Mistral 7B  │
   │   (uvicorn :8000)  │  HTTP API   │    (port 11434)          │
   └──────────┬──────────┘              └─────────────────────────┘
              │
   ┌──────────┴──────────┐
   │   ChromaDB (embed)  │  ← vector store (RAG)
   │   SQLite            │  ← chat history, PIN
   └─────────────────────┘
```

All services run in Docker containers. Model lives in a persistent Docker volume — never in git.

---

## 📁 Project Structure

```
dravis/
├── frontend/          # React + Vite (TypeScript)
│   └── src/
│       ├── components/   # Chat, Docs, Quiz, Settings, PIN, Voice
│       └── utils/api.ts  # API client
├── backend/           # FastAPI (Python 3.11)
│   ├── main.py           # API routes
│   ├── config.py         # Configuration
│   ├── models/           # LLM providers (Ollama, OpenAI, Mock, GGUF)
│   ├── rag/              # Document parsing + ChromaDB RAG
│   ├── quiz/             # Quiz generation
│   ├── speech/           # Whisper STT
│   ├── db/               # SQLite + ChromaDB managers
│   └── utils/            # Language detection, PIN hashing
├── landing/           # One-click download landing page
├── docker-compose.yml # Full stack orchestration
├── Dockerfile.backend # FastAPI container
├── Dockerfile.frontend # nginx + React build
├── nginx.conf         # Proxy config
├── start.sh           # Linux/Mac launcher
├── START.bat          # Windows launcher
└── k8s/               # Kubernetes manifests (coming soon)
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

```env
# LLM
OLLAMA_MODEL=mistral:7b-instruct   # or mistral, llama3, etc.
OLLAMA_BASE_URL=http://ollama:11434

# Optional OpenAI fallback
OPENAI_ENABLED=false
OPENAI_API_KEY=your_key_here

# Mock provider (always-on fallback for testing)
MOCK_ENABLED=true
```

---

## 🧑‍💻 Local Development (without Docker)

```bash
# Backend
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m backend.main

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000/api` in `frontend/.env.local`.

---

## 📦 GitHub Codespaces

Click **"Code" → "Codespaces" → "Create codespace"** on the repo page.  
The `.devcontainer` will auto-install Ollama and pull Mistral 7B on first open.  
Choose a **4-core / 16 GB** machine type when prompted.

---

## 🛣️ Roadmap

- [x] FastAPI backend + React frontend
- [x] RAG with ChromaDB + sentence-transformers
- [x] Quiz generation
- [x] Multilingual support (EN/HI/Hinglish)
- [x] PIN authentication
- [x] Docker Compose (nginx + backend + Ollama)
- [x] NVIDIA GPU support
- [x] Download landing page
- [ ] Kubernetes manifests
- [ ] Whisper STT in Docker
- [ ] Streaming responses

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ using FastAPI · React · Ollama · Mistral 7B · ChromaDB · Docker*
