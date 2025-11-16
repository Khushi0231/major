# backend/rag/document_parser.py
from pypdf import PdfReader
import docx
import os

def extract_pdf(path):
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        content = page.extract_text() or ""
        pages.append({"page": i+1, "text": content})
    return pages

def extract_docx(path):
    doc = docx.Document(path)
    text = "\n".join([p.text for p in doc.paragraphs if p.text])
    return [{"page": 1, "text": text}]

def extract_text_generic(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path)
    elif ext == ".docx":
        return extract_docx(path)
    elif ext in [".txt", ".md"]:
        t = open(path, "r", encoding="utf-8", errors="ignore").read()
        return [{"page": 1, "text": t}]
    else:
        raise Exception(f"Unsupported file type: {ext}")


def chunk_text_for_storage(pages, chunk_size=1000, overlap=200):
    """
    pages: list of {"page": int, "text": str}
    returns: list of (chunk_text, metadata_dict)
    metadata contains source filename must be added by caller
    """
    out_chunks = []
    for p in pages:
        text = p.get("text", "")
        page_num = p.get("page", 1)
        # naive chunking by characters (fast)
        start = 0
        L = len(text)
        while start < L:
            end = min(start + chunk_size, L)
            chunk = text[start:end].strip()
            if chunk:
                out_chunks.append((chunk, {"page": page_num}))
            # move forward with overlap
            start = end - overlap if (end - overlap) > start else end
    return out_chunks
