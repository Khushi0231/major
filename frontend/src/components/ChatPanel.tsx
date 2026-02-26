import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { sendMessage, exportChatHistory, uploadFile } from "../utils/api";
import './ChatPanel.css';

const STORAGE_KEY = "dravis_chat_threads";

interface Message {
  sender: "user" | "ai";
  text: string;
  timestamp: string;
}

interface ChatPanelProps {
  setStatus: React.Dispatch<React.SetStateAction<"online" | "offline">>;
  sessionId: string;
  onFirstMessage: (title: string) => void;
}

const QUICK_START = [
  "Explain Newton's laws like I'm 12",
  "Summarize my uploaded documents",
  "Create a 5-question quiz on World War II",
  "What is machine learning?",
];

export default function ChatPanel({ setStatus, sessionId, onFirstMessage }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [useDocuments, setUseDocuments] = useState(false);
  const [mode, setMode] = useState<"normal" | "exam_prep" | "practice" | "vocabulary">("normal");
  const [uploadStatus, setUploadStatus] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) { setMessages([]); return; }
    try {
      const parsed = JSON.parse(raw);
      setMessages(parsed[sessionId] || []);
    } catch { setMessages([]); }
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const persistMessages = (next: Message[]) => {
    setMessages(next);
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : {};
      parsed[sessionId] = next;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
    } catch { }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const trimmed = input.trim();
    const userMsg: Message = { sender: "user", text: trimmed, timestamp: new Date().toISOString() };
    const newMessages = [...messages, userMsg];
    persistMessages(newMessages);
    setInput("");
    setLoading(true);

    if (messages.filter(m => m.sender === "user").length === 0) {
      onFirstMessage(trimmed.slice(0, 60));
    }

    try {
      const res = await sendMessage(trimmed, useDocuments, mode, sessionId);
      setStatus("online");
      persistMessages([...newMessages, {
        sender: "ai",
        text: res.response || "No response",
        timestamp: new Date().toISOString(),
      }]);
    } catch {
      setStatus("offline");
      persistMessages([...newMessages, {
        sender: "ai",
        text: "Connection lost. Please ensure the backend is running (gateway at http://localhost:8080)",
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadStatus(`Uploading ${file.name}...`);
    try {
      const res = await uploadFile(file);
      if (res?.success !== false) {
        setUploadStatus(`✓ ${file.name} indexed (${res.chunks} chunks)`);
        setUseDocuments(true); // auto-enable RAG
        setTimeout(() => setUploadStatus(""), 4000);
      }
    } catch {
      setUploadStatus("Upload failed");
      setTimeout(() => setUploadStatus(""), 3000);
    }
    e.target.value = "";
  };

  const handleClear = () => {
    if (confirm("Clear this conversation?")) persistMessages([]);
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <h1 className="chat-title">Chat</h1>
          <select value={mode} onChange={(e) => setMode(e.target.value as any)} className="mode-select">
            <option value="normal">Normal</option>
            <option value="exam_prep">Exam Prep</option>
            <option value="practice">Practice</option>
            <option value="vocabulary">Vocabulary</option>
          </select>
        </div>
        <div className="chat-header-right">
          <label className="rag-toggle">
            <input type="checkbox" checked={useDocuments} onChange={(e) => setUseDocuments(e.target.checked)} />
            <span>RAG</span>
          </label>
          <button onClick={() => exportChatHistory(sessionId)} className="btn-icon" title="Export">📥</button>
          <button onClick={handleClear} className="btn-icon" title="Clear">🗑</button>
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="avatar-large">D</div>
            <h2>What are we studying today?</h2>
            <p>Ask questions, upload documents, or generate quizzes — all offline.</p>
            <div className="quick-start-grid">
              {QUICK_START.map((item, idx) => (
                <button key={idx} onClick={() => setInput(item)} className="quick-start-btn">{item}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, idx) => (
          <div key={idx} className={`message ${m.sender}`}>
            {m.sender === "ai" && <div className="message-avatar">D</div>}
            <div className="message-bubble">
              {m.sender === "ai" ? (
                <ReactMarkdown className="message-md">{m.text}</ReactMarkdown>
              ) : (
                <div className="message-text">{m.text}</div>
              )}
            </div>
            {m.sender === "user" && <div className="message-avatar user">You</div>}
          </div>
        ))}

        {loading && (
          <div className="message ai">
            <div className="message-avatar">D</div>
            <div className="message-bubble">
              <div className="typing-indicator"><span /><span /><span /></div>
            </div>
          </div>
        )}
      </div>

      {/* Upload Status */}
      {uploadStatus && (
        <div className={`upload-toast ${uploadStatus.startsWith("✓") ? "success" : ""}`}>
          {uploadStatus}
        </div>
      )}

      {/* Input */}
      <div className="chat-input-container">
        <div className="input-row">
          <button className="attach-btn" onClick={() => fileRef.current?.click()} title="Upload document">
            📎
          </button>
          <input ref={fileRef} type="file" accept=".pdf,.docx,.pptx,.txt,.md" onChange={handleFileUpload} hidden />
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Ask anything..."
            rows={1}
            disabled={loading}
            className="chat-input"
          />
          <button onClick={handleSend} disabled={!input.trim() || loading} className="send-btn">
            {loading ? "..." : "↑"}
          </button>
        </div>
        <div className="input-hint">
          {useDocuments ? "🔗 RAG enabled — answers grounded in your documents" : "DRAVIS runs 100% offline"}
        </div>
      </div>
    </div>
  );
}
