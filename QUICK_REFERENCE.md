# Quick Reference - DRAVIS Troubleshooting

## 🚀 Quick Start

### 1. Start Ollama (if not running)
```powershell
ollama serve
```

### 2. Start Backend
```powershell
cd c:\Users\jerry\Documents\GitHub\major
& ".\venv\Scripts\Activate.ps1"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Frontend
```powershell
cd c:\Users\jerry\Documents\GitHub\major\frontend
npm run dev
```

### 4. Access at
http://localhost:5173

---

## ✅ Verification Checklist

Run these commands to verify everything is working:

```powershell
# Check Ollama is running
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3

# Check Backend is running
Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 3

# Check Frontend is running
Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3

# Test Chat API
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"message":"Hi","use_documents":false,"mode":"normal"}' `
  -TimeoutSec 30
$response.Content | ConvertFrom-Json
```

---

## 🎛️ Sidebar Controls

- **Menu Button (☰)** - Top left in top bar
  - Click to collapse/expand sidebar
  - Smooth animation (300ms)
  - Shows icons when collapsed
  - Shows text when expanded

- **New Chat Button** - In sidebar
  - Creates new chat session
  - Visible as "+ New Chat" when expanded
  - Visible as "+" when collapsed

- **Session List** - Below new chat button
  - Shows recent chat sessions
  - Click to switch sessions
  - Right-click delete button appears on hover (when expanded)

- **Tab Navigation** - Top of sidebar
  - Chat (💬)
  - Docs (📚)
  - Quiz (📝)

---

## 🔧 Common Issues & Fixes

### Issue: "Model not loaded yet"
```powershell
# Check Ollama is running
& {
  $tags = curl -s http://localhost:11434/api/tags | ConvertFrom-Json
  if ($tags.models) {
    "Models available:"
    $tags.models | ForEach-Object { "  - " + $_.name }
  } else {
    "No models! Run: ollama pull llama3"
  }
}

# Or manually:
ollama list
ollama pull llama3
```

### Issue: "Connection refused on port 8000"
```powershell
# Kill existing Python processes
Get-Process python | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Start backend again
cd c:\Users\jerry\Documents\GitHub\major
& ".\venv\Scripts\Activate.ps1"
python -m uvicorn backend.main:app --port 8000
```

### Issue: "Port 5173 already in use"
```powershell
# Find process using port 5173
Get-NetTCPConnection -LocalPort 5173 | Get-Process

# Kill it
Get-Process node | Stop-Process -Force

# Restart frontend
cd frontend
npm run dev
```

### Issue: Sidebar not toggling
1. Open browser dev tools: F12
2. Check Console tab for errors
3. Clear browser cache: Ctrl+Shift+Delete
4. Reload page: Ctrl+R
5. Try clicking menu button again

---

## 📊 Performance Tips

1. **Faster responses:** Use smaller models
   ```powershell
   ollama pull phi         # Fastest (~7B params)
   ollama pull mistral:7b  # Good balance (~7B params)
   ollama pull llama3      # Best quality (~8B params, slower)
   ```

2. **Streaming responses:** (In development)
   - Currently waits for full response
   - Soon: will show answer as it's generated

3. **Multiple documents:** 
   - RAG is optimized for ~100 documents
   - Larger collections may be slower

---

## 🔍 Logs & Debugging

### Backend Logs
```powershell
# View real-time logs
Get-Content "c:\Users\jerry\Documents\GitHub\major\dravis_data\logs\dravis.log" -Tail 20 -Wait

# Last 50 lines
Get-Content "c:\Users\jerry\Documents\GitHub\major\dravis_data\logs\dravis.log" -Tail 50
```

### Frontend Logs
```
Browser Console (F12 → Console tab)
- Shows React errors
- Shows API call responses
- Shows network requests
```

### Check LLM Status
```powershell
# In browser console:
fetch('http://localhost:8000/').then(r => r.json()).then(d => console.log(d))

# Should show:
# {
#   "status": "Backend running",
#   "llm_available": true,
#   "version": "1.0.0"
# }
```

---

## 🎯 Feature Quick Test

### Test Chat
1. Click "Chat" tab (should already be open)
2. Type: "What is your name?"
3. Should respond in 5-30 seconds (depending on model)

### Test Documents
1. Click "📚 Documents" or "Docs" tab
2. Click "Upload File"
3. Select any PDF, DOCX, or PPTX file
4. Should show in list after uploading

### Test Quiz
1. Upload a document (optional)
2. Click "📝 Quiz" or "Quiz" tab
3. Enter topic (e.g., "Python")
4. Click "Generate"
5. Should show quiz questions

### Test Settings
1. Click "⚙️" button in top right (or click gear icon when sidebar expanded)
2. Can set PIN, toggle theme, export chat history

---

## 🆘 Emergency Commands

```powershell
# Stop everything
Get-Process python, node | Stop-Process -Force

# Wait
Start-Sleep -Seconds 3

# Start fresh (from major folder)
& ".\venv\Scripts\Activate.ps1"
python -m uvicorn backend.main:app --port 8000 &
cd frontend; npm run dev

# Access at: http://localhost:5173
```

---

## 📚 Useful Links

- **Ollama Website:** https://ollama.ai
- **Model Zoo:** https://ollama.ai/library
- **FastAPI Docs:** http://localhost:8000/docs (when running)
- **Vite Dev Server:** http://localhost:5173 (when running)

---

**Last Updated:** Dec 9, 2025  
**Version:** 1.0.0  
**Status:** ✅ All systems operational
