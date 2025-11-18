import React, { useEffect, useState } from "react";
import { uploadFile, listDocs, deleteDoc } from "../utils/api";

interface Document {
  document_id: string;
  document_name: string;
  upload_time: string;
  chunk_count: number;
}

export default function DocumentsPanel({ setStatus }: { setStatus: (s: string) => void }) {
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
      if (res.success) {
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
      const res = await deleteDoc(docId);
      if (res.success) {
        await reload();
        setStatus("online");
      }
    } catch (error) {
      console.error("Delete error:", error);
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Upload Card */}
      <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Upload Document</h3>
        <div className="flex gap-3">
          <label className="flex-1 cursor-pointer">
            <input
              type="file"
              onChange={onChoose}
              accept=".pdf,.docx,.pptx,.txt,.md,.jpg,.jpeg,.png,.bmp,.py,.java,.cpp,.js,.json"
              className="hidden"
            />
            <div className="border-2 border-dashed border-gray-600 rounded-lg px-4 py-8 text-center hover:border-gray-500 transition-colors">
              <div className="text-gray-400">
                {selected ? `📄 ${selected.name}` : "📁 Click to select file"}
              </div>
            </div>
          </label>
          <button
            onClick={onUpload}
            disabled={!selected || uploading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 self-end"
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </div>

      {/* Documents Grid */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">
          Documents ({documents.length})
        </h3>
        {documents.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-5xl mb-4">📚</div>
            <p>No documents yet</p>
            <p className="text-sm mt-2">Upload your first document to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className="bg-gray-800/30 border border-gray-700/50 rounded-lg p-4 hover:bg-gray-800/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white truncate">{doc.document_name}</div>
                    <div className="text-sm text-gray-400 mt-1">
                      {doc.chunk_count} chunks
                    </div>
                  </div>
                  <button
                    onClick={() => onDelete(doc.document_id, doc.document_name)}
                    className="ml-3 px-3 py-1.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
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
