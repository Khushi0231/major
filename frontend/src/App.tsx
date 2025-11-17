import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import DocumentsPanel from "./components/DocumentsPanel";
import VoiceControls from "./components/VoiceControls";
import QuizPanel from "./components/QuizPanel";

export default function App() {
  const [active, setActive] = useState<"chat" | "docs" | "quiz" | "settings">("chat");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [status, setStatus] = useState<"online" | "offline">("offline");

  useEffect(() => {
    document.documentElement.classList.toggle("light", theme === "light");
  }, [theme]);

  return (
    <div className="flex h-screen bg-gray-950 text-white font-inter">
      <aside className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col">
        <Sidebar active={active} setActive={setActive} theme={theme} setTheme={setTheme} status={status} />
      </aside>
      <main className="flex-1 flex flex-col relative bg-gray-950">
        <header className="flex items-center justify-between p-6 border-b border-gray-800 bg-gray-950">
          <div>
            <h2 className="text-pink-400 text-lg font-bold tracking-tight">DRAVIS – Offline Chat</h2>
            <div className="text-xs text-gray-400">Your offline study assistant (Local LLM!)</div>
          </div>
          <div className="flex items-center gap-4">
            <span className={`rounded px-2 py-1 text-xs ${status === "online" ? "bg-green-700" : "bg-gray-700"} font-semibold`}>
              {status === "online" ? "Online" : "Offline"}
            </span>
            <button
              className="bg-gray-800 px-2 py-1 rounded text-xs border border-pink-600 text-pink-300 hover:bg-pink-900 transition"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? "🌙" : "☀️"}
            </button>
          </div>
        </header>
        <section className="flex-1 overflow-y-auto px-2 sm:px-6 py-4">
          {active === "chat" && <ChatPanel setStatus={setStatus} />}
          {active === "docs" && <DocumentsPanel />}
          {active === "quiz" && <QuizPanel />}
          {active === "settings" && <div className="p-6 bg-gray-900 rounded-lg text-center text-gray-300">Settings coming soon!</div>}
        </section>
        <VoiceControls />
      </main>
    </div>
  );
}
