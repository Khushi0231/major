# DRAVIS Quick Start Guide

## ✅ Setup Complete!

All dependencies have been installed and the project is ready to run.

## 🚀 Running the Application

### Step 1: Start Backend Server

Open a terminal in the project root and run:

```powershell
.\backend\venv\Scripts\python.exe backend\main.py
```

The backend will start on `http://localhost:8000`

### Step 2: Start Frontend

Open another terminal and run:

```powershell
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000` (or another port if 3000 is busy)

### Step 3: Access DRAVIS

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## 📝 Features Available

### ✅ Working Features:
1. **Chat Interface** - Basic chat (without LLM model file)
2. **Document Upload** - Upload PDF, DOCX, PPTX, TXT files
3. **Document Management** - View and delete uploaded documents
4. **Quiz Generation** - Generate quizzes from topics
5. **Settings** - PIN lock, theme toggle
6. **Chat History** - View and export chat history

### ⚠️ Requires Model File:
- **LLM Chat** - Needs Mistral 7B Q4_K_M model file in `backend/models/`
- **Speech-to-Text** - Whisper models will download automatically on first use

## 🔧 Model Setup (Optional)

To enable full LLM chat functionality:

1. Download Mistral 7B Q4_K_M model:
   - Visit: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
   - Download: `mistral-7b-instruct-v0.2.Q4_K_M.gguf`
   - Place in: `backend/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf`

2. Install llama-cpp-python (if not already):
   ```powershell
   .\backend\venv\Scripts\python.exe -m pip install llama-cpp-python
   ```

## 🎯 Quick Test

1. **Test Backend**: Visit http://localhost:8000 - Should show `{"status": "Backend running", ...}`
2. **Test Frontend**: Visit http://localhost:3000 - Should show DRAVIS interface
3. **Upload Document**: Go to Documents tab, upload a PDF or TXT file
4. **Chat**: Go to Chat tab, type a message (will work even without model file, but responses will be limited)

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

