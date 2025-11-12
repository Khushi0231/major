export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Document {
  id: string;
  name: string;
  uploadedAt: string;
}

export interface ChatRequest {
  message: string;
  useRag: boolean;
  documents?: string[];
}

export interface ChatResponse {
  response: string;
  citations?: string[];
  sources?: string[];
}

export interface UploadResponse {
  documentId: string;
  fileName: string;
  status: 'success' | 'error';
  message: string;
}
