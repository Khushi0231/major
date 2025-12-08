# DRAVIS Quick Start Guide

## ✅ Setup Complete!

All dependencies have been installed and the project is ready to run.

## 🚀 Running the Application

### Step 1: (Optional) Start Ollama

DRAVIS automatically races the local GGUF build and Ollama. If you want the faster Ollama backend:

```powershell
ollama serve
ollama pull mistral:7b
```

Keep this terminal open. Skip this step if you only want the bundled llama-cpp build.

### Step 2: Start Backend Server

```powershell
.\backend\venv\Scripts\python.exe backend\main.py
```

The backend listens on `http://127.0.0.1:8000`. Logs and data live under `dravis_data/`.

### Step 3: Start Frontend

```powershell
cd frontend
npm run dev
```

The Vite dev server defaults to `http://localhost:3000`. Pass `-- --host` if you need LAN access.

### Step 3: Access DRAVIS

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## 📝 Features Available

### ✅ Working Features:
1. **Chat Interface** - Collapsible sidebar, multi-session history, Markdown export
2. **Document Upload & RAG** - PDFs, slides, docs, code, and OCR images (1 GB limit)
3. **Quiz Studio** - MCQ, True/False, fill-in-the-blank, short answer with difficulty levels
4. **Speech Tools** - Whisper / faster-whisper integration for STT
5. **Security & Settings** - PIN gate, light/dark theme persistence, chat export

### ⚠️ Requires Model File / Ollama:
- **LLM Chat** - Needs _either_ the GGUF file in `backend/models/` **or** a running Ollama model
- **Speech-to-Text** - Whisper models download automatically on first run

## 🔧 Model Setup

### Option A – Built-in llama-cpp (offline only)
1. Download `mistral-7b-instruct-v0.2.Q4_K_M.gguf`
   from [TheBloke on Hugging Face](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF).
2. Place the file in `backend/models/`.
3. Ensure `llama-cpp-python` is installed (already listed in `backend/requirements.txt`).

### Option B – Ollama fallback / turbo mode
1. Install [Ollama](https://ollama.ai).
2. Run `ollama serve` once per boot.
3. Pull one of: `ollama pull mistral:7b` (preferred) or any local model you want.
4. DRAVIS will automatically call whichever backend responds first.

## 🎯 Quick Test

1. **Test Backend**: Visit http://localhost:8000 - Should show `{"status": "Backend running", ...}`
2. **Test Frontend**: Visit http://localhost:3000 - Should show DRAVIS interface
3. **Upload Document**: Go to Documents tab, upload a PDF or TXT file
4. **Chat**: Go to Chat tab, type a message. If no LLM is available you’ll see a friendly warning.

## 📊 Current Status

- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed  
- ✅ Backend server can start
- ✅ Frontend can start
- ⚠️ LLM model file needed for full chat functionality
- ✅ Document processing ready
- ✅ Vector database ready
- ✅ All API endpoints implemented

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Ensure virtual environment is activated
- Check `backend/dravis_data/logs/dravis.log` for errors

### Frontend won't start
- Check if port 3000 is available
- Run `npm install` in frontend directory
- Check browser console for errors

### Chat not working
- LLM model file is optional - basic functionality works without it
- To enable full chat, download and place model file as described above

## 📞 Next Steps

1. Start both servers (backend + frontend)
2. Open browser to frontend URL
3. Explore the interface:
   - Upload documents
   - Try quiz generation
   - Test chat (basic mode works without model)
   - Configure settings (PIN, theme)

Enjoy using DRAVIS! 🚀

