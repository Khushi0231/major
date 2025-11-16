import React, { useEffect, useRef, useState } from "react";
import { sendMessage } from "../utils/api";

export default function ChatPanel({ setStatus }: any) {
  const [messages, setMessages] = useState<{sender:"user"|"ai", text:string}[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement|null>(null);

  useEffect(()=> {
    if(scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  },[messages]);

  async function handleSend(){
    if(!input.trim()) return;
    const user = { sender: "user" as const, text: input };
    setMessages(m=>[...m,user]);
    setInput("");
    setLoading(true);

    const res = await sendMessage(input, false);
    setLoading(false);
    if(res && res.response){
      setStatus("online");
      setMessages(m=>[...m,{sender:"ai",text:res.response}]);
    } else {
      setStatus("offline");
      setMessages(m=>[...m,{sender:"ai",text: res.detail || "No response from LLM"}]);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
        <div>
          <div style={{fontWeight:700}}>Conversation</div>
          <div className="kv">Ask DRAVIS questions or load documents</div>
        </div>
        <div>
          <button className="btn small">Clear</button>
        </div>
      </div>

      <div ref={scrollRef} className="chat-window mt-4">
        {messages.map((m,i)=>(
          <div key={i} className={`msg ${m.sender==="user"?"user":"ai"}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="msg ai">⏳ Generating...</div>}
      </div>

      <div className="input-bar mt-4">
        <div className="input-box">
          <input placeholder="Ask anything or attach a doc..." value={input} onChange={e=>setInput(e.target.value)}
            onKeyDown={(e)=>{ if(e.key==="Enter") handleSend()}} />
        </div>
        <button className="btn small" onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}