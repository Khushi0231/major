import React from "react";

export default function Sidebar({ active, setActive, theme, setTheme, status }: any) {
  return (
    <div className="flex flex-col h-full">
      <div className="mb-6">
        <div style={{display:"flex",alignItems:"center",gap:12}}>
          <div style={{width:48,height:48,background:"#16a34a",borderRadius:10}} />
          <div>
            <div style={{fontWeight:800,fontSize:18}}>DRAVIS</div>
            <div className="kv">Offline Study Assistant</div>
          </div>
        </div>
      </div>

      <nav className="mb-6">
        <button className={`btn small w-full mb-2 ${active==="chat"?"border-accent-2":""}`} onClick={()=>setActive("chat")}>Chat</button>
        <button className={`btn small w-full mb-2 ${active==="docs"?"border-accent-2":""}`} onClick={()=>setActive("docs")}>Documents</button>
        <button className={`btn small w-full mb-2 ${active==="quiz"?"border-accent-2":""}`} onClick={()=>setActive("quiz")}>Quiz Generator</button>
        <button className={`btn small w-full mb-2 ${active==="settings"?"border-accent-2":""}`} onClick={()=>setActive("settings")}>Settings</button>
      </nav>

      <div className="mt-auto">
        <div className="kv mb-3">Mode</div>
        <div className="flex gap-2 mb-4">
          <button className="btn small">Normal</button>
          <button className="btn small">Exam</button>
          <button className="btn small">Practice</button>
        </div>

        <div className="kv mb-2">Theme</div>
        <div className="flex gap-2">
          <button className="btn small" onClick={()=>setTheme("dark")}>Dark</button>
          <button className="btn small" onClick={()=>setTheme("light")}>Light</button>
        </div>

        <div className="kv mt-6">LLM Status</div>
        <div style={{marginTop:8}}>
          <div className="doc-item">
            <div>
              <div style={{fontWeight:700}}>Local LLM</div>
              <div className="kv">{ status==="online" ? "Loaded" : "Not loaded" }</div>
            </div>
            <div style={{color: status==="online" ? "#4ade80" : "#f87171", fontWeight:700}}>
              { status==="online" ? "ONLINE" : "OFFLINE" }
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}