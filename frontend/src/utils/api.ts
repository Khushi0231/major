// ─── DRAVIS - API Client ────────────────────────────
// Desktop: localhost:8080 | Mobile: user's desktop IP
// Configurable via Settings → Backend URL
function getApiBase(): string {
  return localStorage.getItem('dravis_api_base')
    || import.meta.env.VITE_API_BASE
    || 'http://127.0.0.1:8080';
}
const API_BASE = getApiBase();

// ─── Chat Service (/api/chat/) ──────────────────────

export async function sendMessage(
  message: string,
  useDocuments: boolean,
  mode: string,
  sessionId?: string,
): Promise<{ response: string; language?: string; mode?: string; provider?: string }> {
  const res = await fetch(`${API_BASE}/api/chat/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      use_documents: useDocuments,
      mode,
      session_id: sessionId,
    }),
  });
  if (!res.ok) throw new Error("Chat failed");
  return res.json();
}

export async function exportChatHistory(sessionId?: string): Promise<void> {
  const url = sessionId
    ? `${API_BASE}/api/chat/export?session_id=${sessionId}`
    : `${API_BASE}/api/chat/export`;
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error("Export failed");
  const blob = await res.blob();
  const a = document.createElement("a");
  a.href = window.URL.createObjectURL(blob);
  a.download = `chat_export_${Date.now()}.md`;
  a.click();
  window.URL.revokeObjectURL(a.href);
}

// ─── Document Service (/api/documents/) ─────────────

export async function uploadFile(
  file: File,
): Promise<{ chunks: number; success: boolean; document_id?: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Upload failed");
  const data = await res.json();
  return { chunks: data.chunks, success: data.success !== false, document_id: data.document_id };
}

export async function listDocs(): Promise<
  Array<{
    document_id: string;
    document_name: string;
    file_size: number;
    chunk_count: number;
    status: string;
    created_at: string;
  }>
> {
  const res = await fetch(`${API_BASE}/api/documents/list`);
  if (!res.ok) throw new Error("Failed to list documents");
  const data = await res.json();
  return data.documents || [];
}

export async function deleteDoc(docId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Delete failed");
}

// ─── Quiz Service (/api/quiz/) ──────────────────────

export async function generateQuiz(
  topic: string,
  difficulty: string,
  quizType: string,
  fromDocuments: boolean,
): Promise<{ questions: any[] }> {
  const res = await fetch(`${API_BASE}/api/quiz/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic,
      difficulty,
      quiz_type: quizType,
      use_documents: fromDocuments,
    }),
  });
  if (!res.ok) throw new Error("Quiz generation failed");
  return res.json();
}

// ─── Auth Service (/api/auth/) ──────────────────────

export async function setPIN(pin: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/api/auth/pin/set`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin }),
  });
  if (!res.ok) throw new Error("Failed to set PIN");
  return res.json();
}

export async function verifyPIN(pin: string): Promise<{ verified: boolean }> {
  const res = await fetch(`${API_BASE}/api/auth/pin/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin }),
  });
  if (!res.ok) throw new Error("Verification failed");
  return res.json();
}

export async function checkPINExists(): Promise<{ exists: boolean }> {
  const res = await fetch(`${API_BASE}/api/auth/pin/exists`);
  if (!res.ok) throw new Error("Check failed");
  return res.json();
}

// ─── Speech Service (/api/speech/) ──────────────────

export async function speechToText(audioBlob: Blob): Promise<{ text: string; language?: string }> {
  const formData = new FormData();
  formData.append("audio_file", audioBlob, "recording.wav");
  const res = await fetch(`${API_BASE}/api/speech/transcribe`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Speech-to-text failed");
  return res.json();
}

// ─── Health (Gateway) ───────────────────────────────

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}
