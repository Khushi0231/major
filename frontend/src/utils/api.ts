const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function sendMessage(message: string, userag = false) {
  try {
    const r = await fetch(`${BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, userag })
    });
    return await r.json();
  } catch (e) {
    return {
      response: "Network error",
      source: "error",
      detail: String(e)
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
  const r = await fetch(`${BASE}/api/documents`);
  if (!r.ok) return [];
  const data = await r.json();
  return data.docs || [];
}

export async function deleteDoc(filename: string) {
  const r = await fetch(`${BASE}/api/documents/${encodeURIComponent(filename)}`, {
    method: "DELETE"
  });
  return r.json();
}
