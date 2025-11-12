# DRAVIS - Offline Claude-Style Intelligent Study Assistant

**Dynamic Reasoning AI for Virtual Intelligent Study** - A complete offline desktop application featuring Claude-inspired UI, full voice I/O, persistent memory, and advanced RAG capabilities.

## 🎯 Key Features

✅ **100% Offline** - No internet required, all processing local  
✅ **Claude-Like Interface** - Exact UI replication with React + TailwindCSS  
✅ **Full Voice I/O** - Speech recognition + Text-to-speech  
✅ **Advanced RAG** - Document parsing + Vector search + Citations  
✅ **Persistent Memory** - Auto-save chat history + embeddings  
✅ **Multi-Format Support** - PDF, DOCX, PPTX, images, audio, video, code  
✅ **Windows-First** - Optimized for Windows (Tauri Desktop App)  

## 🏗️ Architecture

```
DRAVIS/
├── frontend/                    # Tauri + React + TypeScript
│   ├── src/
│   │   ├── components/         # ChatPanel, Sidebar, VoiceControls
│   │   ├── pages/              # Settings, Chat
│   │   └── utils/              # API calls, helpers
│   ├── package.json
│   └── tauri.conf.json
│
├── backend/                     # Python + FastAPI
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration
│   ├── models/                 # Ollama handler, embeddings
│   ├── rag/                    # Document parser, retriever
│   ├── speech/                 # Whisper.cpp STT, Piper TTS
│   ├── db/                     # ChromaDB, SQLite
│   └── requirements.txt        # Python dependencies
│
├── data/                        # Persistent data
│   ├── models/                 # LLM weights
│   ├── vectors/                # ChromaDB embeddings
│   ├── logs/                   # Application logs
│   ├── cache/                  # Temporary files
│   └── uploads/                # User documents
│
└── README.md
```

## 📋 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|----------|
| **Frontend** | Tauri + React + TS + TailwindCSS | UI/UX |
| **Backend** | Python + FastAPI | API & Logic |
| **LLM** | Ollama (Llama2/Mixtral/Phi) | Local Inference |
| **Embeddings** | nomic-embed-text (Ollama) | Vector Search |
| **Vector DB** | ChromaDB | Local Storage |
| **DB** | SQLite | Chat History |
| **Speech** | Whisper.cpp + Piper | Voice I/O |
| **Parsing** | PyMuPDF, python-docx, pytesseract | Document Ingestion |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- [Ollama](https://ollama.ai) installed
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/Khushi0231/major.git
cd major
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Activate venv
# On Windows:
venv\\Scripts\\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Download LLM Model (via Ollama)

```bash
# Ensure Ollama is running
oollama pull llama2     # Or: mixtral, neural-chat, phi
oollama pull nomic-embed-text
```

### 4. Start Backend

```bash
cd backend
python main.py
# Backend runs on: http://localhost:8000
```

### 5. Frontend Setup

```bash
cd frontend
npm install
```

### 6. Run Frontend (Development)

```bash
npm run tauri dev
```

### 7. Build for Production

```bash
npm run tauri build
```

## 📡 API Endpoints

### Core Chat
- `POST /chat` - Process text or voice message
- `POST /upload` - Upload documents
- `GET /list-docs` - List indexed documents

### Voice
- `POST /stt` - Speech to text (requires audio file)
- `POST /tts` - Text to speech

### System
- `GET /healthcheck` - Service status

## 🎤 Example Usage

### Chat Flow

```python
# 1. Upload document
POST /upload
Body: file=mydocument.pdf

# 2. Ask question about document
POST /chat
{
    "message": "What is the main topic of this document?",
    "use_rag": true,
    "context": "mydocument"
}

Response:
{
    "response": "The document discusses...",
    "citations": [{"source": "mydocument.pdf", "page": 3}],
    "confidence": 0.95
}
```

### Voice Interaction

```
User: [clicks 🎤] → Records audio
  ↓
Backend: /stt → Converts to text
  ↓
Backend: /chat → Processes query
  ↓
Backend: /tts → Generates speech
  ↓
UI: [clicks 🔊] → Plays response
```

## 🔧 Configuration

Edit `backend/config.py`:

```python
# LLM Selection
OLLAMA_MODEL = "llama2"        # mixtral, neural-chat, phi
OLLAMA_EMBED_MODEL = "nomic-embed-text"

# API
API_HOST = "127.0.0.1"
API_PORT = 8000

# Data
DATA_DIR = "./data"
```

## 📁 File Structure

```
backend/
├── main.py                     # FastAPI application
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
│
├── models/
│   ├── __init__.py
│   ├── ollama_handler.py      # LLM interface
│   └── embedding_manager.py   # Embedding generation
│
├── rag/
│   ├── __init__.py
│   ├── document_parser.py     # PDF, DOCX, PPTX parsing
│   └── retriever.py           # Vector search & ranking
│
├── speech/
│   ├── __init__.py
│   ├── whisper_handler.py     # Speech recognition
│   └── tts_handler.py         # Text-to-speech
│
├── db/
│   ├── __init__.py
│   ├── chroma_store.py        # Vector DB interface
│   └── sqlite_manager.py      # Chat history DB
│
└── utils/
    ├── logger.py              # Logging setup
    └── error_handler.py       # Error handling
```

## 🎨 Frontend Features

### Components
- **ChatPanel** - Main chat interface
- **Sidebar** - Document list + history
- **VoiceControls** - 🎤 Record & 🔊 Play buttons
- **Settings** - Model selection, temperature, voice toggle
- **FileUpload** - Drag-and-drop or click to upload

### UI/UX
- Claude-style responsive layout
- Dark mode support
- Real-time message streaming
- Typing indicators
- Toast notifications for errors

## ⚙️ Advanced Setup

### Use Different LLM Models

```bash
# Fast (mobile-friendly)
oollama pull phi

# Balanced
oollama pull neural-chat

# Powerful (requires more VRAM)
oollama pull mixtral:8x7b
oollama pull llama2:70b
```

### Enable GPU Acceleration

Ollama automatically detects CUDA/Metal. To force:

```bash
GPU_ENABLE=1 ollama serve
```

### Customize Temperature & Settings

In `backend/config.py`:

```python
LLM_TEMPERATURE = 0.7  # 0=deterministic, 1=creative
LLM_TOP_P = 0.95
LLM_TOP_K = 40
```

## 🧪 Testing

### Test Backend

```bash
curl http://localhost:8000/healthcheck

# Should return: {"status": "operational", "service": "DRAVIS Backend"}
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat \
  -d "message=Hello, how are you?" \
  -d "use_rag=false"
```

## �� Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Load LLM | 2-10s | First load, then cached |
| Chat Response | 1-5s | Depends on model size |
| Document Parse | 500ms-2s | Depends on file size |
| Vector Search | 50-200ms | Cached results |

## 🐛 Troubleshooting

### "Connection refused" on backend

```bash
# Ensure backend is running
cd backend && python main.py
```

### "Ollama not found" error

```bash
# Install Ollama from https://ollama.ai
# Then run:
oollama serve
```

### GPU not detected

```bash
# Check CUDA/Metal installation
oollama ps
# Should show GPU in the output
```

## 📝 Development Notes

### Adding New Document Types

Edit `backend/rag/document_parser.py`:

```python
from filetype_parser import parse_xyz

def parse_file(filepath):
    if filepath.endswith('.xyz'):
        return parse_xyz(filepath)
    # ...
```

### Implementing Custom RAG

Edit `backend/rag/retriever.py`:

```python
def custom_retriever(query):
    # Implement custom ranking logic
    results = vector_search(query, top_k=5)
    return rerank_results(results)
```

## �� Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🙏 Acknowledgments

- Inspired by Claude AI
- Built with FastAPI, Tauri, React
- Models via Ollama
- Vector search via ChromaDB

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Open GitHub Issue
3. Check existing discussions

---

**DRAVIS** - Your offline AI study companion. Work smarter, study better. 🚀
