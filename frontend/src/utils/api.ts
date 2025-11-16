const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function sendMessage(message: string, use_rag = false) {
  try {
    const r = await fetch(`${BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, use_rag })
    });
    return await r.json();
  } catch (e) {
    return { response: `Network error: ${String(e)}`, source: "error", detail: String(e) };
  }
}

export async function uploadFile(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`${BASE}/api/upload`, { method: "POST", body: fd });
  return r.json();
}

export async function listDocs() {
  const r = await fetch(`${BASE}/api/documents`);
  return r.ok ? r.json() : { docs: [] };
}

export async function deleteDoc(filename: string) {
  const r = await fetch(`${BASE}/api/documents/${encodeURIComponent(filename)}`, { method: "DELETE" });
  return r.json();
}