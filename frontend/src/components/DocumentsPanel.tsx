import React, { useEffect, useState } from "react";
import { uploadFile, listDocs, deleteDoc } from "../utils/api";

export default function DocumentsPanel({ setStatus }: any){
  const [files, setFiles] = useState<string[]>([]);
  const [selected, setSelected] = useState<File|null>(null);

  useEffect(()=>{ reload(); },[]);

  async function reload(){ 
    const data = await listDocs();
    setFiles(data.docs || []);
  }

  async function onChoose(e: any){
    setSelected(e.target.files[0]);
  }

  async function onUpload(){
    if(!selected) return;
    const res = await uploadFile(selected);
    await reload();
    setStatus("online");
  }

  async function onDelete(name: string){
    await deleteDoc(name);
    reload();
  }

  return (
    <div className="p-4 bg-white/5 rounded">
      <div style={{fontWeight:700}}>Documents</div>
      <div className="kv mb-3">Upload and manage documents used for context</div>

      <div style={{marginTop:8,marginBottom:8}}>
        <input type="file" onChange={onChoose} />
        <button className="btn small ml-2" onClick={onUpload}>Upload</button>
      </div>

      <div style={{marginTop:12}}>
        {files.length===0 && <div className="kv">No documents uploaded</div>}
        {files.map(f=>(
          <div key={f} className="doc-item">
            <div>
              <div style={{fontWeight:700}}>{f}</div>
              <div className="kv">uploaded</div>
            </div>
            <div style={{display:"flex",gap:8}}>
              <button className="btn small" onClick={()=>onDelete(f)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}