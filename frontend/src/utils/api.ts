const API_BASE = "http://localhost:8000/api";

export async function sendMessage(
  message: string,
  useDocuments: boolean,
  mode: string
): Promise<{ response: string }> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      use_documents: useDocuments,
      mode,
    }),
  });

  if (!res.ok) throw new Error("Chat failed");
  return res.json();
}

export async function uploadFile(file: File): Promise<{ chunks: number; success: boolean }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Upload failed");
  const data = await res.json();
  return { chunks: data.chunks, success: data.success };
}

export async function listDocs(): Promise<Array<{ document_id: string; document_name: string; upload_time: string; chunk_count: number }>> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("Failed to list documents");
  const data = await res.json();
  return (data.documents || []).map((doc: any) => ({
    document_id: doc.document_id,
    document_name: doc.document_name,
    upload_time: doc.upload_time,
    chunk_count: doc.chunk_count
  }));
}

export async function deleteDoc(docName: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${docName}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Delete failed");
}

export async function generateQuiz(
  topic: string,
  difficulty: string,
  quizType: string,
  fromDocuments: boolean
): Promise<{ questions: any[] }> {
  const res = await fetch(`${API_BASE}/quiz/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic,
      difficulty,
      quiz_type: quizType,
      from_documents: fromDocuments,
    }),
  });

  if (!res.ok) throw new Error("Quiz generation failed");
  return res.json();
}

export async function setPIN(pin: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/pin/set`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin }),
  });

  if (!res.ok) throw new Error("Failed to set PIN");
  return res.json();
}

export async function verifyPIN(pin: string): Promise<{ verified: boolean }> {
  const res = await fetch(`${API_BASE}/pin/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin }),
  });

  if (!res.ok) throw new Error("Verification failed");
  return res.json();
}

export async function checkPINExists(): Promise<{ exists: boolean }> {
  const res = await fetch(`${API_BASE}/pin/exists`);
  if (!res.ok) throw new Error("Check failed");
  return res.json();
}

export async function exportChatHistory(): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/export`, {
    method: "POST",
  });

  if (!res.ok) throw new Error("Export failed");

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `chat_history_${Date.now()}.md`;
  a.click();
  window.URL.revokeObjectURL(url);
}
