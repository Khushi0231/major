import React from "react";

interface SidebarProps {
  active: string;
  setActive: (tab: "chat" | "docs" | "quiz" | "settings") => void;
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light") => void;
  status: "online" | "offline";
  sessions: { id: string; title: string; timestamp: number }[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onClose?: () => void;
  onOpenSettings: () => void;
}

export default function Sidebar({
  active,
  setActive,
  theme,
  setTheme,
  status,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onClose,
  onOpenSettings,
}: SidebarProps) {
  const menuItems = [
    { id: "chat", label: "Chat", icon: "💬" },
    { id: "docs", label: "Documents", icon: "📚" },
    { id: "quiz", label: "Quiz", icon: "📝" },
  ];

  return (
    <div className="flex flex-col h-full bg-[#0c111f] text-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-900 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
            D
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-widest">Offline</div>
            <h1 className="text-lg font-semibold text-white">DRAVIS</h1>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-900 rounded-lg transition-colors text-gray-400"
            title="Collapse sidebar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-b border-gray-900 space-y-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 transition-colors"
        >
          <span>＋</span> New chat
        </button>
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="w-full flex items-center justify-between px-4 py-2.5 rounded-lg bg-gray-900 text-sm text-gray-300 hover:bg-gray-800 transition-colors"
        >
          <span>Theme</span>
          <span>{theme === "dark" ? "🌙 Dark" : "☀️ Light"}</span>
        </button>
      </div>

      {/* Recent chats */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-2">
        <div className="text-xs uppercase tracking-wider text-gray-500 px-2 mb-2">Recent Chats</div>
        {sessions.map((session) => (
          <button
            key={session.id}
            onClick={() => {
              onSelectSession(session.id);
              setActive("chat");
            }}
            className={`w-full text-left px-3 py-2.5 rounded-lg transition-all ${
              session.id === activeSessionId
                ? "bg-gray-900 text-white border border-gray-800"
                : "text-gray-400 hover:bg-gray-900/60"
            }`}
          >
            <div className="text-sm font-medium truncate">{session.title || "New chat"}</div>
            <div className="text-[11px] text-gray-500">Offline • {new Date(session.timestamp).toLocaleTimeString()}</div>
          </button>
        ))}
        {sessions.length === 0 && (
          <div className="text-xs text-gray-500 px-3 py-6 text-center bg-gray-900/40 rounded-lg">
            No chats yet
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-900 space-y-3">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${status === "online" ? "bg-green-400" : "bg-gray-600"}`}
            />
            <span>{status === "online" ? "Connected" : "Offline mode"}</span>
          </div>
          <span className="text-gray-600">v1.0</span>
        </div>
        <button
          onClick={() => {
            setActive("settings");
            onOpenSettings();
          }}
          className="w-full flex items-center justify-between px-4 py-2.5 rounded-lg bg-gray-900 hover:bg-gray-800 text-sm text-gray-300 transition-colors"
        >
          <span>Profile & Security</span>
          <span>⚙️</span>
        </button>
      </div>
    </div>
  );
}
