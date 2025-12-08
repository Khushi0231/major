import React, { useEffect, useRef, useState } from "react";
import { sendMessage, exportChatHistory } from "../utils/api";
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
  "Summarize this PDF I just uploaded",
  "Create a 5-question MCQ quiz on World War II",
  "Transcribe my audio note and create flashcards",
];

export default function ChatPanel({ setStatus, sessionId, onFirstMessage }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [useDocuments, setUseDocuments] = useState(false);
  const [mode, setMode] = useState<"normal" | "exam_prep" | "practice" | "vocabulary">("normal");
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      setMessages([]);
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      setMessages(parsed[sessionId] || []);
    } catch {
      setMessages([]);
    }
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const persistMessages = (nextMessages: Message[]) => {
    setMessages(nextMessages);
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : {};
      parsed[sessionId] = nextMessages;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
    } catch (err) {
      console.error("Failed to persist chat session", err);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const trimmed = input.trim();
    const userMessage: Message = {
      sender: "user",
      text: trimmed,
      timestamp: new Date().toISOString(),
    };

    const newMessages = [...messages, userMessage];
    persistMessages(newMessages);
    setInput("");
    setLoading(true);

    if (messages.filter((m) => m.sender === "user").length === 0) {
      onFirstMessage(trimmed.slice(0, 60));
    }

    try {
      const res = await sendMessage(trimmed, useDocuments, mode);
      setStatus("online");
      const aiMessage: Message = {
        sender: "ai",
        text: res.response || "No response",
        timestamp: new Date().toISOString(),
      };
      persistMessages([...newMessages, aiMessage]);
    } catch (err) {
      setStatus("offline");
      const errorMessage: Message = {
        sender: "ai",
        text: "❌ Connection lost. Please ensure the backend is running at http://localhost:8000",
        timestamp: new Date().toISOString(),
      };
      persistMessages([...newMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    if (confirm("Clear all messages in this chat?")) {
      persistMessages([]);
    }
  };

  const handleExport = async () => {
    try {
      await exportChatHistory();
    } catch (err) {
      alert("Export failed. Check backend logs.");
    }
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <h1 className="chat-title">DRAVIS Chat</h1>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as any)}
            className="mode-select"
          >
            <option value="normal">Normal</option>
            <option value="exam_prep">Exam Prep</option>
            <option value="practice">Practice</option>
            <option value="vocabulary">Vocabulary</option>
          </select>
        </div>
        <div className="chat-header-right">
          <label className="rag-toggle">
            <input
              type="checkbox"
              checked={useDocuments}
              onChange={(e) => setUseDocuments(e.target.checked)}
            />
            <span>Use RAG</span>
          </label>
          <button onClick={handleExport} className="btn-icon" title="Export Chat">
            📥
          </button>
          <button onClick={handleClear} className="btn-icon" title="Clear Chat">
            🗑️
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="avatar-large">D</div>
            <h2>What are we studying today?</h2>
            <p>DRAVIS runs fully offline. Upload notes, ask for summaries, or generate quizzes.</p>
            <div className="quick-start-grid">
              {QUICK_START.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(item)}
                  className="quick-start-btn"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, idx) => (
          <div key={idx} className={`message ${m.sender}`}>
            {m.sender === "ai" && <div className="message-avatar">D</div>}
            <div className="message-bubble">
              <div className="message-text">{m.text}</div>
            </div>
            {m.sender === "user" && <div className="message-avatar user">You</div>}
          </div>
        ))}

        {loading && (
          <div className="message ai">
            <div className="message-avatar">D</div>
            <div className="message-bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="chat-input-container">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Ask me anything..."
          rows={1}
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="send-btn"
        >
          {loading ? "⏳" : "➤"}
        </button>
        <div className="input-hint">
          DRAVIS runs 100% offline. Double-check critical answers.
        </div>
      </div>
    </div>
  );
}
