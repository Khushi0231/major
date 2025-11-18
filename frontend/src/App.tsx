import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import DocumentsPanel from "./components/DocumentsPanel";
import QuizPanel from "./components/QuizPanel";
import SettingsPanel from "./components/SettingsPanel";
import PINLock from "./components/PINLock";

type View = "chat" | "docs" | "quiz" | "settings";

interface ChatSession {
  id: string;
  title: string;
  timestamp: number;
}

export default function App() {
  const [activeView, setActiveView] = useState<View>("chat");
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    const saved = localStorage.getItem("dravis_theme");
    return (saved as "dark" | "light") || "dark";
  });
  const [status, setStatus] = useState<"online" | "offline">("offline");
  const [isLocked, setIsLocked] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState<ChatSession[]>(() => {
    const stored = localStorage.getItem("dravis_sessions");
    return stored ? JSON.parse(stored) : [{ id: "session-1", title: "New chat", timestamp: Date.now() }];
  });
  const [activeSessionId, setActiveSessionId] = useState(sessions[0]?.id || "session-1");

  useEffect(() => {
    document.documentElement.classList.toggle("light", theme === "light");
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("dravis_sessions", JSON.stringify(sessions));
  }, [sessions]);

  const handleUnlock = () => setIsLocked(false);

  const handleNewChat = () => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}`,
      title: "New chat",
      timestamp: Date.now(),
    };
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    setActiveView("chat");
  };

  const handleUpdateSessionTitle = (title: string) => {
    setSessions((prev) =>
      prev.map((session) =>
        session.id === activeSessionId ? { ...session, title, timestamp: Date.now() } : session
      )
    );
  };

  if (isLocked) {
    return <PINLock onUnlock={handleUnlock} />;
  }

  return (
    <div className="flex h-screen bg-[#05060b] text-gray-100 overflow-hidden">
      {/* Sidebar */}
      <div
        className={`transition-all duration-300 ease-in-out border-r border-gray-900 bg-[#0c111f] ${
          sidebarOpen ? "w-72" : "w-0"
        } overflow-hidden`}
      >
        {sidebarOpen && (
          <Sidebar
            active={activeView}
            setActive={setActiveView}
            theme={theme}
            setTheme={(t) => {
              setTheme(t);
              localStorage.setItem("dravis_theme", t);
            }}
            status={status}
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={(id) => {
              setActiveSessionId(id);
              setActiveView("chat");
            }}
            onNewChat={handleNewChat}
            onClose={() => setSidebarOpen(false)}
            onOpenSettings={() => setActiveView("settings")}
          />
        )}
      </div>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 border-b border-gray-900 bg-[#05060b]/95 backdrop-blur flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen((prev) => !prev)}
              className="p-2 hover:bg-gray-900/60 rounded-lg transition-colors text-gray-400"
              title="Toggle sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">DRAVIS</div>
              <h1 className="text-lg font-semibold text-white capitalize">{activeView}</h1>
            </div>
          </div>
          <div
            className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs ${
              status === "online"
                ? "bg-green-500/15 text-green-400 border border-green-500/30"
                : "bg-gray-900 text-gray-500 border border-gray-800"
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${status === "online" ? "bg-green-400 animate-pulse" : "bg-gray-600"}`} />
            {status === "online" ? "Online" : "Offline"}
          </div>
        </header>

        <section className="flex-1 overflow-hidden bg-[#05060b]">
          {activeView === "chat" && (
            <ChatPanel
              setStatus={setStatus}
              sessionId={activeSessionId}
              onFirstMessage={handleUpdateSessionTitle}
            />
          )}
          {activeView === "docs" && <DocumentsPanel setStatus={setStatus} />}
          {activeView === "quiz" && <QuizPanel />}
          {activeView === "settings" && <SettingsPanel theme={theme} setTheme={setTheme} />}
        </section>
      </main>
    </div>
  );
}
