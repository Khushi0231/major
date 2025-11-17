import React from "react";

export default function Sidebar({
  active,
  setActive,
  theme,
  setTheme,
  status,
}: {
  active: string;
  setActive: (tab: any) => void;
  theme: string;
  setTheme: (s: any) => void;
  status: string;
}) {
  return (
    <nav className="flex-1 flex flex-col pt-4 space-y-2">
      <div className="text-lg font-bold text-pink-400 px-4 pb-4">DRAVIS</div>
      <button
        className={`px-4 py-2 text-left rounded transition ${
          active === "chat" ? "bg-pink-900 text-white" : "bg-gray-800 text-pink-200"
        }`}
        onClick={() => setActive("chat")}
      >
        💬 Chat
      </button>
      <button
        className={`px-4 py-2 text-left rounded transition ${
          active === "docs" ? "bg-pink-900 text-white" : "bg-gray-800 text-pink-200"
        }`}
        onClick={() => setActive("docs")}
      >
        📄 Documents
      </button>
      <button
        className={`px-4 py-2 text-left rounded transition ${
          active === "quiz" ? "bg-pink-900 text-white" : "bg-gray-800 text-pink-200"
        }`}
        onClick={() => setActive("quiz")}
      >
        📝 Quiz
      </button>
      <button
        className={`px-4 py-2 text-left rounded transition ${
          active === "settings" ? "bg-pink-900 text-white" : "bg-gray-800 text-pink-200"
        }`}
        onClick={() => setActive("settings")}
      >
        ⚙️ Settings
      </button>
      <div className="flex-1" />
      <div className="p-4 text-xs text-gray-400">Status: {status}</div>
      <div className="p-4 text-xs text-gray-600">Theme:&nbsp;
        <button
          className={`px-1 py-0.5 rounded ${theme === "dark" ? "bg-pink-700" : "bg-gray-700"} text-white`}
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? "Dark" : "Light"}
        </button>
      </div>
    </nav>
  );
}
