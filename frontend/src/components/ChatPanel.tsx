import React, { useEffect, useRef, useState } from "react";
import { sendMessage, exportChatHistory } from "../utils/api";

interface Message {
  sender: "user" | "ai";
  text: string;
  timestamp?: string;
}

export default function ChatPanel({ setStatus }: { setStatus: (s: string) => void }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [useDocuments, setUseDocuments] = useState(false);
  const [mode, setMode] = useState<"normal" | "exam_prep" | "practice" | "vocabulary">("normal");
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage: Message = {
      sender: "user",
      text: input.trim(),
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput("");
    setLoading(true);
    
    try {
      const res = await sendMessage(currentInput, useDocuments, mode);
      setStatus("online");
      
      const aiMessage: Message = {
        sender: "ai",
        text: res.response || "No response",
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      setStatus("offline");
      const errorMessage: Message = {
        sender: "ai",
        text: "Sorry, I'm having trouble connecting. Please try again.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Minimal Controls Bar */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-gray-800/50 bg-[#0f0f23]/50 flex-shrink-0">
        <div className="flex items-center gap-4">
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as any)}
            className="bg-gray-800/50 border border-gray-700/50 text-white text-sm px-3 py-1.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="normal">Normal</option>
            <option value="exam_prep">Exam Prep</option>
            <option value="practice">Practice</option>
            <option value="vocabulary">Vocabulary</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={useDocuments}
              onChange={(e) => setUseDocuments(e.target.checked)}
              className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500"
            />
            <span>Use Documents</span>
          </label>
        </div>
        <div className="flex items-center gap-3">
          {messages.length > 0 && (
            <>
              <button
                onClick={async () => {
                  try {
                    await exportChatHistory();
                  } catch (err) {
                    alert("Failed to export");
                  }
                }}
                className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
              >
                Export
              </button>
              <button
                onClick={() => setMessages([])}
                className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
              >
                Clear
              </button>
            </>
          )}
        </div>
      </div>

      {/* Messages Area - ChatGPT Style */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-6"
        style={{ scrollbarWidth: "thin" }}
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl mb-6">
              D
            </div>
            <h2 className="text-3xl font-semibold text-white mb-3">How can I help you today?</h2>
            <p className="text-gray-400 text-lg">Ask me anything or upload documents for context</p>
          </div>
        )}
        
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-4 animate-fade-in ${m.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.sender === "ai" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0 mt-1">
                D
              </div>
            )}
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                m.sender === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800/50 text-gray-100 border border-gray-700/50"
              }`}
            >
              <div className="whitespace-pre-wrap break-words leading-relaxed">{m.text}</div>
            </div>
            {m.sender === "user" && (
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-gray-400 text-xs flex-shrink-0 mt-1">
                You
              </div>
            )}
          </div>
        ))}
        
        {loading && (
          <div className="flex gap-4 animate-fade-in">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0 mt-1">
              D
            </div>
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area - ChatGPT Style */}
      <div className="border-t border-gray-800/50 bg-[#0f0f23]/80 backdrop-blur-sm p-4 flex-shrink-0">
        <div className="max-w-3xl mx-auto w-full">
          <div className="relative flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                className="w-full bg-gray-800/50 border border-gray-700/50 text-white rounded-2xl px-4 py-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500"
                placeholder="Message DRAVIS..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={1}
                disabled={loading}
                style={{ minHeight: "52px", maxHeight: "200px" }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 shadow-lg shadow-blue-500/20"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            DRAVIS can make mistakes. Check important info.
          </p>
        </div>
      </div>
    </div>
  );
}
