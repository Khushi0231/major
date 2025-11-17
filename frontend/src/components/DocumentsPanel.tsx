import React, { useEffect, useState } from "react";
import { uploadFile, listDocs, deleteDoc } from "../utils/api";

export default function DocumentsPanel({ setStatus }: { setStatus: (s: string) => void }) {
  const [files, setFiles] = useState<string[]>([]);
  const [selected, setSelected] = useState<File | null>(null);

  async function reload() {
    const docs = await listDocs();
    setFiles(docs);
  }

  useEffect(() => { reload(); }, []);

  async function onChoose(e: any) {
    setSelected(e.target.files[0]);
  }
  async function onUpload() {
    if (!selected) return;
    const res = await uploadFile(selected);
    await reload();
    setStatus("online");
  }
  async function onDelete(name: string) {
    await deleteDoc(name);
    await reload();
    setStatus("online");
  }

  return (
    <div className="p-4 bg-gray-950 rounded-xl">
      <div className="font-bold text-pink-400 mb-2">Documents</div>
      <div className="text-xs text-gray-400 mb-3">Upload and manage documents used for context</div>
      <div className="flex gap-2 mb-3">
        <input type="file" onChange={onChoose} className="bg-gray-900 border border-pink-400 text-pink-200 p-2 rounded"/>
        <button className="bg-pink-700 text-white px-4 py-2 rounded transition hover:bg-pink-600" onClick={onUpload}>Upload</button>
      </div>
      <div className="my-3">
        {files.length === 0 && <div className="text-pink-300">No documents uploaded</div>}
        {files.map(f =>
          <div key={f} className="flex justify-between items-center bg-gray-800 px-4 py-2 rounded mb-2">
            <div className="font-bold text-pink-300">{f}</div>
            <button className="text-xs bg-pink-900 text-white px-2 py-1 rounded" onClick={() => onDelete(f)}>Delete</button>
          </div>
        )}
      </div>
    </div>
  );
}
