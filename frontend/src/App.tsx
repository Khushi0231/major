import { useState, useEffect } from 'react';
import ChatPanel from './components/ChatPanel';
import DocumentsPanel from './components/DocumentsPanel';
import QuizPanel from './components/QuizPanel';
import SettingsPanel from './components/SettingsPanel';
import Sidebar from './components/Sidebar';
import PINLock from './components/PINLock';
import './App.css';

const SESSIONS_KEY = 'dravis_chat_sessions';

interface Session {
  id: string;
  title: string;
  timestamp: number;
}

type ActiveTab = 'chat' | 'docs' | 'quiz' | 'settings';

function App() {
  // Always start locked — PINLock handles both set & verify
  const [isLocked, setIsLocked] = useState(true);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [status, setStatus] = useState<'online' | 'offline'>('offline');
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Load theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('dravis-theme') as 'dark' | 'light' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-color-scheme', theme);
    localStorage.setItem('dravis-theme', theme);
  }, [theme]);

  // Load sessions
  useEffect(() => {
    loadSessions();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8080';
      const response = await fetch(`${apiBase}/api/health`);
      if (response.ok) {
        setStatus('online');
      } else {
        setStatus('offline');
      }
    } catch (error) {
      setStatus('offline');
    }
  };

  const loadSessions = () => {
    const raw = localStorage.getItem(SESSIONS_KEY);
    if (!raw) {
      const newSession = createNewSession();
      setSessions([newSession]);
      setActiveSessionId(newSession.id);
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      setSessions(parsed);
      setActiveSessionId(parsed[0]?.id || createNewSession().id);
    } catch {
      const newSession = createNewSession();
      setSessions([newSession]);
      setActiveSessionId(newSession.id);
    }
  };

  const createNewSession = (): Session => {
    return {
      id: `session_${Date.now()}`,
      title: 'New Chat',
      timestamp: Date.now(),
    };
  };

  const handleNewChat = () => {
    const newSession = createNewSession();
    const updated = [newSession, ...sessions];
    setSessions(updated);
    setActiveSessionId(newSession.id);
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(updated));
    setActiveTab('chat');
  };

  const handleSessionSelect = (sessionId: string) => {
    setActiveSessionId(sessionId);
    setActiveTab('chat');
  };

  const handleSessionDelete = (sessionId: string) => {
    const updated = sessions.filter(s => s.id !== sessionId);
    setSessions(updated);
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(updated));
    if (activeSessionId === sessionId && updated.length > 0) {
      setActiveSessionId(updated[0].id);
    }
  };

  if (isLocked) {
    return <PINLock onUnlock={() => setIsLocked(false)} />;
  }

  return (
    <div className={`app-container theme-${theme}`}>
      <div className="app-layout">
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSessionSelect={handleSessionSelect}
          onSessionDelete={handleSessionDelete}
          onNewChat={handleNewChat}
          status={status}
          collapsed={!sidebarOpen}
          onCollapsedChange={(collapsed) => setSidebarOpen(!collapsed)}
        />

        <div className="main-container">
          <div className="top-bar">
            <button
              className="menu-btn"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              ☰
            </button>
            <div className="top-bar-right">
              <span className={`status ${status}`}>{status === 'online' ? '🟢' : '🔴'}</span>
              <button
                className="theme-btn"
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              >
                {theme === 'dark' ? '☀️' : '🌙'}
              </button>
              <button
                className="settings-btn"
                onClick={() => setActiveTab('settings')}
              >
                ⚙️
              </button>
            </div>
          </div>

          <div className="content">
            {activeTab === 'chat' && (
              <ChatPanel sessionId={activeSessionId} setStatus={setStatus} onFirstMessage={(title) => {
                const updated = sessions.map(s =>
                  s.id === activeSessionId ? { ...s, title } : s
                );
                setSessions(updated);
                localStorage.setItem(SESSIONS_KEY, JSON.stringify(updated));
              }} />
            )}
            {activeTab === 'docs' && <DocumentsPanel setStatus={setStatus} />}
            {activeTab === 'quiz' && <QuizPanel />}
            {activeTab === 'settings' && (
              <SettingsPanel
                theme={theme}
                setTheme={setTheme}
                onLockApp={() => setIsLocked(true)}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
