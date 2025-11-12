
import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<string[]>([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const newMsg = { role: 'user', content: input };
    setMessages([...messages, newMsg]);
    setInput('');
    setLoading(true);
    
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, use_rag: documents.length > 0 })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-panel">
          <div className="messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                <div className="content">{msg.content}</div>
              </div>
            ))}
            {loading && <div className="message assistant"><div className="typing">...</div></div>}
          </div>
          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything..."
            />
            <button onClick={sendMessage} disabled={loading}>Send</button>
          </div>
        </div>
        <div className="sidebar">
          <h3>Documents ({documents.length})</h3>
          <div className="doc-list">
            {documents.map((doc, i) => (
              <div key={i} className="doc-item">{doc}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
