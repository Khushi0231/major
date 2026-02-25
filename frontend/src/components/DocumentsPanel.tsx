import React, { useEffect, useState } from "react";
import { uploadFile, listDocs, deleteDoc } from "../utils/api";
import './DocumentsPanel.css';

interface Document {
  document_id: string;
  document_name: string;
  upload_time: string;
  chunk_count: number;
}

export default function DocumentsPanel({
  setStatus,
}: {
  setStatus: React.Dispatch<React.SetStateAction<"online" | "offline">>;
}) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selected, setSelected] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  function onChoose(e: React.ChangeEvent<HTMLInputElement>) {
    setSelected(e.target.files?.[0] ?? null);
  }

  async function reload() {
    try {
      const docs = await listDocs();
      setDocuments(docs);
    } catch (error) {
      console.error("Failed to load documents:", error);
    }
  }

  useEffect(() => {
    reload();
  }, []);

  async function onUpload() {
    if (!selected) return;

    setUploading(true);
    try {
      const res = await uploadFile(selected);
      if (res && res.success !== false) {
        await reload();
        setStatus("online");
        setSelected(null);
      } else {
        alert("Upload failed");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function onDelete(docId: string, docName: string) {
    if (!confirm(`Delete "${docName}"?`)) return;

    try {
      await deleteDoc(docId);
      await reload();
      setStatus("online");
    } catch (error) {
      console.error("Delete error:", error);
    }
  }

  return (
    <div className="documents-panel">
      {/* Upload Section */}
      <div className="documents-header">
        <span className="documents-title">Upload Document</span>
        <label className="upload-btn">
          <input
            type="file"
            onChange={onChoose}
            accept=".pdf,.docx,.pptx,.txt,.md,.jpg,.jpeg,.png,.bmp,.py,.java,.cpp,.js,.json"
            className="upload-input"
          />
          {selected ? `📄 ${selected.name}` : "📁 Choose file"}
        </label>
        <button
          onClick={onUpload}
          disabled={!selected || uploading}
          className="upload-btn"
          style={{ opacity: !selected || uploading ? 0.5 : 1, cursor: !selected || uploading ? 'not-allowed' : 'pointer' }}
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {/* Documents List */}
      <div className="documents-content">
        <div className="documents-title" style={{ marginBottom: '12px' }}>
          Documents ({documents.length})
        </div>
        {documents.length === 0 ? (
          <div className="empty-documents">
            <div className="empty-icon">📚</div>
            <p>No documents yet</p>
            <p style={{ fontSize: '12px', marginTop: '8px' }}>Upload your first document to get started</p>
          </div>
        ) : (
          <div className="documents-list">
            {documents.map((doc) => (
              <div key={doc.document_id} className="document-item">
                <div>
                  <div className="document-name">{doc.document_name}</div>
                  <div className="document-meta">{doc.chunk_count} chunks</div>
                </div>
                <div className="document-actions">
                  <button
                    onClick={() => onDelete(doc.document_id, doc.document_name)}
                    className="doc-btn"
                    style={{ color: '#ef4444' }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
