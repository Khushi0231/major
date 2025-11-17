import { useState } from "react";
import { sendMessage } from "../lib/api";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);

    const res = await sendMessage(input);

    const botMsg = { role: "assistant", text: res.response };
    setMessages((m) => [...m, botMsg]);

    setInput("");
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="loading">⏳ Generating...</div>}
      </div>

      <div className="input-row">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything…"
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
