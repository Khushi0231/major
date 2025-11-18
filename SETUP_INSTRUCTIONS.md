# DRAVIS Setup Instructions

## Complete Feature Implementation

DRAVIS (Dynamic Reasoning AI for Virtual Intelligent Study) is now fully implemented with all required features.

## ✅ Implemented Features

### Core Chat & RAG System
- ✅ Basic Chat with Mistral 7B Q4_K_M quantized model
- ✅ RAG toggle ("Use Documents") to enable/disable document context
- ✅ Chat without documents (general knowledge queries)
- ✅ Conversation history across sessions
- ✅ Export conversations as Markdown files

### Document Ingestion (1GB Capacity)
- ✅ Support for: PDF, DOCX, PPTX, TXT, MD, images (.jpg, .png, .bmp), code files (.py, .java, .cpp, .js, .json)
- ✅ PDF parsing with Docling (fallback to PyMuPDF)
- ✅ Text extraction with metadata preservation
- ✅ ChromaDB vector database storage with sentence-transformers embeddings
- ✅ Document metadata tracking (name, upload time, chunk count)
- ✅ Individual document deletion

### Speech-to-Text (STT)
- ✅ OpenAI Whisper base model integration
- ✅ Microphone input from frontend
- ✅ Audio file upload via API
- ✅ Transcribed text with language detection
- ✅ Real-time transcription display

### Quiz Generation
- ✅ Simple Quizzes: Multiple Choice (MCQ), True/False
- ✅ Advanced Quizzes: Fill-in-the-blank, Short Answer
- ✅ Generate from ingested documents or general topics
- ✅ Difficulty levels (easy, medium, hard)
- ✅ JSON format with questions, options, correct answers, explanations
- ✅ 5-10 questions per quiz

### Study Modes
- ✅ Normal Mode: Standard conversational responses
- ✅ Exam Prep Mode: Concise answers for 10-minute rapid revision
- ✅ Practice Mode: Generate follow-up practice questions
- ✅ Vocabulary Mode: Focus on word meanings, usage, pronunciation

### Language Support
- ✅ English: Full support
- ✅ Hindi: Devanagari script detection, respond in Hindi or English
- ✅ Hinglish: Roman Hindi keyword detection, respond in Hinglish or English
- ✅ Automatic language detection without user selection

### Security & UX
- ✅ 4-Digit PIN Lock with SHA-256 hashing
- ✅ PIN stored in `dravis_data/pin.hash`
- ✅ Dark/Light Mode toggle
- ✅ Theme preference persistence across sessions
- ✅ Chat history persistence
- ✅ Export full conversation as Markdown with timestamps

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 16+
- Windows 10/11 (Mac/Linux ready)
- 8GB-16GB RAM recommended
- Mistral 7B Q4_K_M GGUF model file

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r ../requirements.txt
```

5. **Download Mistral 7B Model:**
   - Download `mistral-7b-instruct-v0.2.Q4_K_M.gguf` from HuggingFace
   - Place it in `backend/models/` directory

6. **Start backend server:**
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

Frontend will run on `http://localhost:3000` (or configured port)

### First Run

1. **Start Backend:**
   - Run `python main.py` in backend directory
   - Wait for "Backend running" message

2. **Start Frontend:**
   - Run `npm run dev` in frontend directory
   - Open browser to frontend URL

3. **Set PIN (Optional):**
   - Go to Settings tab
   - Set a 4-digit PIN if desired
   - PIN will be required on next launch

4. **Upload Documents:**
   - Go to Documents tab
   - Upload PDF, DOCX, PPTX, or other supported files
   - Documents are automatically processed and indexed

5. **Start Chatting:**
   - Go to Chat tab
   - Toggle "Use Documents" to enable RAG
   - Select study mode (Normal, Exam Prep, Practice, Vocabulary)
   - Start asking questions!

## 📁 Directory Structure

```
major/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration
│   ├── models/
│   │   ├── ollama_handler.py      # Mistral 7B handler
│   │   └── embedding_manager.py   # Sentence-transformers
│   ├── rag/
│   │   └── document_parser.py     # Document parsing
│   ├── db/
│   │   ├── chroma_store.py        # ChromaDB wrapper
│   │   └── sqlite_manager.py      # Chat history
│   ├── speech/
│   │   └── whisper_handler.py     # Whisper STT
│   ├── quiz/
│   │   └── quiz_generator.py      # Quiz generation
│   └── utils/
│       ├── language_detector.py   # Language detection
│       └── pin_manager.py         # PIN management
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main app
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx      # Chat interface
│   │   │   ├── DocumentsPanel.tsx # Document management
│   │   │   ├── QuizPanel.tsx      # Quiz interface
│   │   │   ├── VoiceControls.tsx  # STT controls
│   │   │   ├── SettingsPanel.tsx  # Settings
│   │   │   └── PINLock.tsx        # PIN lock screen
│   │   └── utils/
│   │       └── api.ts             # API client
│   └── package.json
│
└── dravis_data/                   # Created on first run
    ├── chroma_db/                 # Vector database
    ├── uploads/                   # Uploaded documents
    ├── logs/                      # Application logs
    ├── dravis.db                  # Chat history
    └── pin.hash                   # PIN hash (if set)
```

## 🔧 Configuration

Edit `backend/config.py` to customize:
- API host/port
- Model paths
- Chunk sizes
- File size limits
- Embedding model

## 📝 API Endpoints

### Chat
- `POST /api/chat` - Send message with RAG and mode support

### Documents
- `POST /api/upload` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### Speech
- `POST /api/stt` - Speech-to-text

### Quiz
- `POST /api/quiz` - Generate quiz

### Chat History
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/export` - Export as Markdown

### PIN
- `POST /api/pin/set` - Set PIN
- `POST /api/pin/verify` - Verify PIN
- `GET /api/pin/exists` - Check if PIN exists

## 🎯 Usage Examples

### Chat with Documents
1. Upload a PDF in Documents tab
2. Go to Chat tab
3. Toggle "Use Documents" ON
4. Ask questions about the document

### Generate Quiz
1. Upload documents (optional)
2. Go to Quiz tab
3. Enter topic
4. Select difficulty and type
5. Toggle "Use Documents" if needed
6. Click "Generate Quiz"

### Speech Input
1. Click "🎤 Record" button
2. Speak your question
3. Click "⏹️ Stop"
4. Transcribed text will be sent to chat

### Export Chat
1. Go to Chat tab
2. Click "💾 Export" button
3. Markdown file will be downloaded

## ⚠️ Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Ensure Python dependencies are installed
- Check that Mistral model file exists in `backend/models/`

### Frontend can't connect
- Verify backend is running on `http://localhost:8000`
- Check CORS settings in `backend/main.py`
- Check browser console for errors

### Documents not uploading
- Check file size (max 1GB)
- Verify file type is supported
- Check `dravis_data/uploads/` directory permissions

### STT not working
- Ensure microphone permissions are granted
- Check that Whisper model is downloaded
- Verify audio format is supported

## 📊 Performance Notes

- First model load: 2-10 seconds
- Chat response: 1-5 seconds (depends on hardware)
- Document processing: 500ms-2s per document
- Vector search: 50-200ms
- STT: 1-3 seconds per audio clip

## 🔒 Security

- PIN is hashed with SHA-256
- No data sent to external servers
- All processing is local
- Documents stored in local `dravis_data/` directory

## 📄 License

MIT License - See LICENSE file

---

**DRAVIS** - Your offline AI study companion! 🚀

