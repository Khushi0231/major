import React, { useEffect, useRef, useState } from "react";
import { uploadFile, listDocs, deleteDoc } from "../utils/api";
import './DocumentsPanel.css';

interface Document {
  document_id: string;
  document_name: string;
  file_size: number;
  chunk_count: number;
  status: string;
  created_at: string;
}

export default function DocumentsPanel({
  setStatus,
}: {
  setStatus: React.Dispatch<React.SetStateAction<"online" | "offline">>;
}) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  async function reload() {
    try {
      const docs = await listDocs();
      setDocuments(docs);
      setStatus("online");
    } catch {
      console.error("Failed to load documents");
    }
  }

  useEffect(() => { reload(); }, []);

  async function handleUpload(file: File) {
    setUploading(true);
    setUploadProgress(`Processing ${file.name}...`);
    try {
      const res = await uploadFile(file);
      if (res?.success !== false) {
        setUploadProgress(`✓ ${file.name} — ${res.chunks} chunks indexed`);
        await reload();
        setTimeout(() => setUploadProgress(""), 3000);
      } else {
        setUploadProgress("Upload failed");
      }
    } catch {
      setUploadProgress("Upload failed — check backend");
    } finally {
      setUploading(false);
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }

  function onFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    e.target.value = "";
  }

  async function onDelete(docId: string, docName: string) {
    if (!confirm(`Delete "${docName}"?`)) return;
    try {
      await deleteDoc(docId);
      await reload();
    } catch {
      console.error("Delete failed");
    }
  }

  function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  }

  return (
    <div className="docs-panel">
      {/* Drop Zone */}
      <div
        className={`drop-zone ${dragging ? "active" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          onChange={onFileSelect}
          accept=".pdf,.docx,.pptx,.txt,.md,.jpg,.jpeg,.png"
          hidden
        />
        <div className="drop-icon">{uploading ? "⏳" : "📄"}</div>
        <div className="drop-title">
          {uploading ? "Processing..." : "Drop file here or click to upload"}
        </div>
        <div className="drop-subtitle">
          PDF, DOCX, PPTX, TXT, MD, Images — up to 50 MB
        </div>
        {uploadProgress && (
          <div className={`drop-status ${uploadProgress.startsWith("✓") ? "success" : ""}`}>
            {uploadProgress}
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="docs-section">
        <div className="docs-section-title">
          Your Documents
          <span className="docs-count">{documents.length}</span>
        </div>

        {documents.length === 0 ? (
          <div className="docs-empty">
            <div className="docs-empty-icon">📚</div>
            <div>No documents yet</div>
            <div className="docs-empty-hint">Upload your study material to enable RAG-powered answers</div>
          </div>
        ) : (
          <div className="docs-grid">
            {documents.map((doc) => (
              <div key={doc.document_id} className="doc-card">
                <div className="doc-card-icon">
                  {doc.document_name.endsWith(".pdf") ? "📕" :
                    doc.document_name.endsWith(".docx") ? "📘" :
                      doc.document_name.endsWith(".pptx") ? "📙" : "📄"}
                </div>
                <div className="doc-card-info">
                  <div className="doc-card-name">{doc.document_name}</div>
                  <div className="doc-card-meta">
                    {doc.chunk_count} chunks · {formatSize(doc.file_size)} ·{" "}
                    <span className={`doc-status ${doc.status}`}>{doc.status}</span>
                  </div>
                </div>
                <button
                  className="doc-delete-btn"
                  onClick={() => onDelete(doc.document_id, doc.document_name)}
                  title="Delete document"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
