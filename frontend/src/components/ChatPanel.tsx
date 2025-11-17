import React, { useEffect, useRef, useState } from "react";
import { sendMessage } from "../utils/api";

export default function ChatPanel({ setStatus }: { setStatus: (s: string) => void }) {
  const [messages, setMessages] = useState<Array<{ sender: "user" | "ai", text: string }>>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages([...messages, { sender: "user", text: input }]);
    setInput("");
    setLoading(true);
    try {
      const res = await sendMessage(input);
      setStatus("online");
      setMessages((m) => [...m, { sender: "ai", text: res.response || "..." }]);
    } catch (err) {
      setStatus("offline");
      setMessages((m) => [...m, { sender: "ai", text: "No response from LLM" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center mb-2 px-1">
        <div className="font-bold text-pink-400">Conversation</div>
        <button
          className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded hover:bg-pink-900 transition"
          onClick={() => setMessages([])}
        >
          Clear
        </button>
      </div>
      <div className="text-xs text-gray-500 pb-1 px-2">Ask DRAVIS questions or load documents</div>
      <div className="flex-1 bg-gray-900 rounded-xl shadow-inner p-4 overflow-y-auto" ref={scrollRef}>
        {messages.map((m, i) => (
          <div
            key={i}
            className={`whitespace-pre-wrap mb-3 flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <span
              className={`px-4 py-2 rounded-2xl max-w-xl break-words ${
                m.sender === "user" ? "bg-pink-700 text-white" : "bg-gray-800 text-pink-200"
              } shadow`}
            >
              {m.text}
            </span>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start pb-3">
            <span className="bg-gray-800 text-pink-300 px-4 py-2 rounded-2xl animate-pulse">Bot is typing…</span>
          </div>
        )}
      </div>
      <div className="flex items-center gap-2 mt-3 px-1">
        <input
          className="flex-1 bg-gray-800 text-white p-3 rounded-xl outline-none border-none"
          placeholder="Type a message…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
        />
        <button
          className="bg-pink-700 hover:bg-pink-600 text-white px-5 py-2 rounded-xl shadow transition"
          onClick={handleSend}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
