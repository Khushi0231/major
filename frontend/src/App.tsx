import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import DocumentsPanel from "./components/DocumentsPanel";
import VoiceControls from "./components/VoiceControls";
import QuizPanel from "./components/QuizPanel";

export default function App(){
  const [active, setActive] = useState<"chat"|"docs"|"quiz"|"settings">("chat");
  const [theme, setTheme] = useState<"dark"|"light">("dark");
  const [status, setStatus] = useState<"online"|"offline">("offline");

  useEffect(()=> {
    document.documentElement.classList.toggle("light", theme==="light");
  },[theme]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Sidebar
          active={active}
          setActive={setActive}
          theme={theme}
          setTheme={setTheme}
          status={status}
        />
      </aside>

      <main className="main-panel">
        <header className="flex items-center justify-between">
          <div>
            <h2 style={{fontSize:20,fontWeight:700}}>DRAVIS — Offline Chat</h2>
            <div className="kv">Your offline study assistant • Local LLM</div>
          </div>
          <div className="kv">Status: <strong style={{color: status==="online"?"#4ade80":"#f87171"}}>{status}</strong></div>
        </header>

        {active==="chat" && <ChatPanel setStatus={setStatus} />}
        {active==="docs" && <DocumentsPanel setStatus={setStatus} />}
        {active==="quiz" && <QuizPanel />}
        {active==="settings" && (
          <div className="p-6 bg-white/5 rounded">Settings coming soon</div>
        )}

        <VoiceControls />
      </main>
    </div>
  );
}