const API_BASE = 'http://localhost:8000/api';

export const apiClient = {
  async chat(message: string, useRag: boolean = true, documents: string[] = []) {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, useRag, documents }),
    });
    return response.json();
  },

  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  async listDocuments() {
    const response = await fetch(`${API_BASE}/list-docs`);
    return response.json();
  },

  async getChatHistory() {
    const response = await fetch(`${API_BASE}/chat-history`);
    return response.json();
  },

  async speak(text: string) {
    const response = await fetch(`${API_BASE}/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return response.blob();
  },

  async transcribe(audioBlob: Blob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    const response = await fetch(`${API_BASE}/stt`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  async getStats() {
    const response = await fetch(`${API_BASE}/stats`);
    return response.json();
  },

  async healthCheck() {
    const response = await fetch(`${API_BASE}/healthcheck`);
    return response.json();
  },
};
