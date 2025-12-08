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
  const [isLocked, setIsLocked] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [status, setStatus] = useState<'online' | 'offline'>('offline');
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('');

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 30000); // Check every 30s
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
      const response = await fetch('/api/health');
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

  const handleFirstMessage = (title: string) => {
    const updated = sessions.map((s) =>
      s.id === activeSessionId ? { ...s, title } : s
    );
    setSessions(updated);
    localStorage.setItem(SESSIONS_KEY, JSON.stringify(updated));
  };

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
    setActiveTab('chat');
  };

  const handleOpenSettings = () => {
    setActiveTab('settings');
  };

  if (isLocked) {
    return <PINLock onUnlock={() => setIsLocked(false)} />;
  }

  return (
    <div className="app">
      <Sidebar
        active={activeTab}
        setActive={setActiveTab}
        theme={theme}
        setTheme={setTheme}
        status={status}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onOpenSettings={handleOpenSettings}
      />
      
      <main className="main-content">
        {activeTab === 'chat' && (
          <ChatPanel
            setStatus={setStatus}
            sessionId={activeSessionId}
            onFirstMessage={handleFirstMessage}
          />
        )}
        
        {activeTab === 'docs' && (
          <DocumentsPanel setStatus={setStatus} />
        )}
        
        {activeTab === 'quiz' && (
          <QuizPanel />
        )}
        
        {activeTab === 'settings' && (
          <SettingsPanel
            theme={theme}
            setTheme={setTheme}
            onLock={() => setIsLocked(true)}
          />
        )}
      </main>
    </div>
  );
}

export default App;
