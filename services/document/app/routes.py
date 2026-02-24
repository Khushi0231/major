"""Document Service - API Routes"""
import os
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import chromadb

from .config import settings
from .database import get_db, DocumentRecord, engine
from .schemas import (
    UploadResponse, DocumentListResponse, DocumentInfo,
    DeleteResponse, QueryRequest, QueryResponse, QueryResult,
    HealthResponse,
)
from . import embeddings, parser

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── ChromaDB client (server mode) ─────────────
_chroma_client = None
_collection = None


def _get_collection():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection
    try:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT,
        )
        _collection = _chroma_client.get_or_create_collection(
            name="documents",
            metadata={"description": "DRAVIS document embeddings"},
        )
        logger.info("Connected to ChromaDB")
        return _collection
    except Exception as e:
        logger.error(f"ChromaDB connection failed: {e}")
        return None


# ─── Upload ─────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate extension
    ext = Path(file.filename or "").suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f".{ext} not supported")

    content = file.file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB)")

    doc_id = str(uuid.uuid4())
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(content)

    # Create DB record
    record = DocumentRecord(
        document_id=doc_id,
        document_name=file.filename,
        file_path=file_path,
        file_size=len(content),
        status="processing",
    )
    db.add(record)
    db.commit()

    try:
        # Parse
        pages = parser.parse_document(file_path)
        chunks = parser.chunk_text(pages, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        if not chunks:
            raise HTTPException(400, "No text extracted")

        # Embed
        texts = [c[0] for c in chunks]
        embs = embeddings.embed_batch(texts)

        valid_chunks, valid_embs = [], []
        for chunk, emb in zip(chunks, embs):
            if emb is not None:
                valid_chunks.append(chunk)
                valid_embs.append(emb)
        if not valid_chunks:
            raise HTTPException(500, "Embedding generation failed")

        # Store in ChromaDB
        collection = _get_collection()
        if collection is None:
            raise HTTPException(503, "ChromaDB unavailable")

        ids = [f"{doc_id}_chunk_{i}" for i in range(len(valid_chunks))]
        documents = [c[0] for c in valid_chunks]
        metadatas = [
            {"document_id": doc_id, "document_name": file.filename, "chunk_index": i, **c[1]}
            for i, c in enumerate(valid_chunks)
        ]
        collection.add(ids=ids, documents=documents, embeddings=valid_embs, metadatas=metadatas)

        # Update DB record
        record.chunk_count = len(valid_chunks)
        record.status = "ready"
        db.commit()

        return UploadResponse(
            success=True,
            document_id=doc_id,
            filename=file.filename or "",
            chunks=len(valid_chunks),
            file_size=len(content),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        record.status = "failed"
        db.commit()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Processing failed: {e}")


# ─── List ───────────────────────────────────────

@router.get("/list", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)):
    rows = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()
    docs = [
        DocumentInfo(
            document_id=r.document_id,
            document_name=r.document_name,
            file_size=r.file_size or 0,
            chunk_count=r.chunk_count or 0,
            status=r.status or "unknown",
            created_at=str(r.created_at) if r.created_at else "",
        )
        for r in rows
    ]
    return DocumentListResponse(documents=docs)


# ─── Delete ─────────────────────────────────────

@router.delete("/{doc_id}", response_model=DeleteResponse)
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    record = db.query(DocumentRecord).filter(
        (DocumentRecord.document_id == doc_id) | (DocumentRecord.document_name == doc_id)
    ).first()
    if not record:
        raise HTTPException(404, f"Document {doc_id} not found")

    # Delete from ChromaDB
    collection = _get_collection()
    if collection:
        try:
            results = collection.get(where={"document_id": record.document_id})
            if results["ids"]:
                collection.delete(ids=results["ids"])
        except Exception as e:
            logger.warning(f"ChromaDB delete warning: {e}")

    # Delete file
    if record.file_path and os.path.exists(record.file_path):
        os.remove(record.file_path)

    # Delete DB record
    db.delete(record)
    db.commit()

    return DeleteResponse(success=True, message=f"Deleted {record.document_name}")


# ─── Query (internal, used by Chat/Quiz) ───────

@router.post("/query", response_model=QueryResponse)
def query_documents(req: QueryRequest):
    """Semantic search across stored document chunks."""
    emb = embeddings.embed_text(req.query)
    if emb is None:
        raise HTTPException(503, "Embedding model not ready")

    collection = _get_collection()
    if collection is None:
        raise HTTPException(503, "ChromaDB unavailable")

    results = collection.query(query_embeddings=[emb], n_results=req.top_k)

    items = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            items.append(QueryResult(
                text=results["documents"][0][i],
                metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                distance=results["distances"][0][i] if results.get("distances") else None,
            ))

    return QueryResponse(results=items)


# ─── Health ─────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health_check():
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            from sqlalchemy import text as sa_text
            conn.execute(sa_text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    chroma_status = "unknown"
    try:
        c = _get_collection()
        chroma_status = "connected" if c is not None else "disconnected"
    except Exception:
        chroma_status = "disconnected"

    overall = "ok" if db_status == "connected" and chroma_status == "connected" else "degraded"
    return HealthResponse(
        status=overall,
        service="document",
        database=db_status,
        chromadb=chroma_status,
        embedding_model=settings.EMBEDDING_MODEL,
    )
