const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export interface ChatRequest {
  message: string;
  use_documents?: boolean;
  mode?: "normal" | "exam_prep" | "practice" | "vocabulary";
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  language?: string;
  mode?: string;
  error?: string;
}

export async function sendMessage(
  message: string,
  useDocuments: boolean = false,
  mode: string = "normal"
): Promise<ChatResponse> {
  try {
    const r = await fetch(`${BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        use_documents: useDocuments,
        mode
      })
    });
    return await r.json();
  } catch (e) {
    return {
      response: "Network error",
      error: String(e)
    };
  }
}

export async function uploadFile(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`${BASE}/api/upload`, {
    method: "POST",
    body: fd
  });
  return r.json();
}

export async function listDocs() {
  try {
    const r = await fetch(`${BASE}/api/documents`);
    if (!r.ok) return [];
    const data = await r.json();
    return data.docs || [];
  } catch (e) {
    return [];
  }
}

export async function deleteDoc(documentId: string) {
  const r = await fetch(`${BASE}/api/documents/${encodeURIComponent(documentId)}`, {
    method: "DELETE"
  });
  return r.json();
}

export async function speechToText(audioFile: File, language?: string) {
  const fd = new FormData();
  fd.append("audio_file", audioFile);
  if (language) {
    fd.append("language", language);
  }
  const r = await fetch(`${BASE}/api/stt`, {
    method: "POST",
    body: fd
  });
  return r.json();
}

export interface QuizRequest {
  topic: string;
  num_questions?: number;
  difficulty?: "easy" | "medium" | "hard";
  quiz_type?: "simple" | "advanced";
  use_documents?: boolean;
}

export async function generateQuiz(req: QuizRequest) {
  const r = await fetch(`${BASE}/api/quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req)
  });
  return r.json();
}

export async function getChatHistory(limit: number = 50) {
  const r = await fetch(`${BASE}/api/chat/history?limit=${limit}`);
  return r.json();
}

export async function exportChatHistory() {
  const r = await fetch(`${BASE}/api/chat/export`, {
    method: "POST"
  });
  if (r.ok) {
    const blob = await r.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dravis_chat_export_${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    return { success: true };
  }
  return { success: false };
}

export async function setPIN(pin: string) {
  const r = await fetch(`${BASE}/api/pin/set`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin })
  });
  return r.json();
}

export async function verifyPIN(pin: string) {
  const r = await fetch(`${BASE}/api/pin/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin })
  });
  return r.json();
}

export async function checkPINExists() {
  const r = await fetch(`${BASE}/api/pin/exists`);
  return r.json();
}
