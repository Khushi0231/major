interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: "chat" | "docs" | "quiz" | "settings") => void;
  sessions: { id: string; title: string; timestamp: number }[];
  activeSessionId: string;
  onSessionSelect: (id: string) => void;
  onSessionDelete: (id: string) => void;
  onNewChat: () => void;
  status: "online" | "offline";
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
}

export default function Sidebar({
  activeTab,
  onTabChange,
  sessions,
  activeSessionId,
  onSessionSelect,
  onSessionDelete,
  onNewChat,
  collapsed = false,
  onCollapsedChange = () => {},
}: SidebarProps) {
  const menuItems = [
    { id: "chat", label: "Chat", icon: "💬" },
    { id: "docs", label: "Docs", icon: "📚" },
    { id: "quiz", label: "Quiz", icon: "📝" },
  ];

  return (
    <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      {/* Header with Collapse Button */}
      <div className="sidebar-header-container">
        <div className="sidebar-header">
          {collapsed ? "D" : "DRAVIS"}
        </div>
        <button
          className="sidebar-collapse-btn"
          onClick={() => onCollapsedChange?.(!collapsed)}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? "→" : "←"}
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id as "chat" | "docs" | "quiz" | "settings")}
            className={`${activeTab === item.id ? "active" : ""}`}
            title={item.label}
          >
            {collapsed ? item.icon : item.label}
          </button>
        ))}
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat} title="New Chat">
        {collapsed ? "+" : "+ New Chat"}
      </button>

      {/* Sessions List */}
      <div className="sessions-list">
        {sessions.map((session) => (
          <button
            key={session.id}
            className={`session-item ${activeSessionId === session.id ? "active" : ""}`}
            onClick={() => onSessionSelect(session.id)}
            title={session.title || "New chat"}
          >
            {!collapsed && (
              <>
                <span className="session-title">
                  {session.title || "New chat"}
                </span>
                <button
                  className="session-delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSessionDelete(session.id);
                  }}
                  title="Delete session"
                >
                  ✕
                </button>
              </>
            )}
            {collapsed && "•"}
          </button>
        ))}
      </div>
    </div>
  );
}
