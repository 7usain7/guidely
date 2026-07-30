from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import glob
from typing import List, Dict, Any
from backend.services.ingestion import load_and_chunk_document
from backend.services.vector_store import vector_store
from backend.models.record import DocumentUploadResponse, DocumentMetadata

router = APIRouter(prefix="/api/documents", tags=["documents"])

SAMPLE_DOCS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "sample-docs")
)

@router.post("/index-all")
def index_all_sample_documents() -> Dict[str, Any]:
    """Indexes all sample documents and purges deleted documents from vector store memory."""
    os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
    doc_files = glob.glob(os.path.join(SAMPLE_DOCS_DIR, "*.*"))
    current_filenames = set(os.path.basename(f) for f in doc_files)

    # Purge deleted documents from vector store memory
    stored_filenames = set(chunk.filename for chunk in vector_store.chunk_store.values())
    deleted_filenames = stored_filenames - current_filenames

    for del_file in deleted_filenames:
        cids_to_del = [cid for cid, chunk in vector_store.chunk_store.items() if chunk.filename == del_file]
        for cid in cids_to_del:
            if cid in vector_store.chunk_store:
                del vector_store.chunk_store[cid]
            if cid in vector_store.embeddings:
                del vector_store.embeddings[cid]
        if del_file in vector_store.doc_hashes:
            del vector_store.doc_hashes[del_file]

    if not doc_files:
        return {
            "message": "No sample documents found. Purged deleted files from memory.",
            "indexed_files": 0,
            "purged_files": list(deleted_filenames)
        }

    indexed_summary = []
    total_chunks = 0
    all_cached_count = 0

    for filepath in doc_files:
        filename, chunks, file_hash = load_and_chunk_document(filepath)
        chunk_count, is_cached = vector_store.index_document(filename, chunks, file_hash)
        total_chunks += chunk_count
        if is_cached:
            all_cached_count += 1
        
        indexed_summary.append({
            "filename": filename,
            "chunks": chunk_count,
            "cache_hit": is_cached
        })

    return {
        "message": f"Successfully indexed {len(indexed_summary)} documents (purged {len(deleted_filenames)} deleted files)",
        "total_documents": len(indexed_summary),
        "total_chunks": total_chunks,
        "all_cache_hit": all_cached_count == len(indexed_summary),
        "purged_files": list(deleted_filenames),
        "files": indexed_summary
    }

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Uploads a document file and indexes its content into the vector store."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided in upload")

    allowed_exts = [".txt", ".md", ".json", ".csv"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension '{ext}'. Allowed: {allowed_exts}")

    os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
    save_path = os.path.join(SAMPLE_DOCS_DIR, file.filename)
    
    content_bytes = await file.read()
    with open(save_path, "wb") as f:
        f.write(content_bytes)

    filename, chunks, file_hash = load_and_chunk_document(save_path)
    chunk_count, is_cached = vector_store.index_document(filename, chunks, file_hash)

    return DocumentUploadResponse(
        filename=filename,
        message=f"Document uploaded and indexed successfully into {chunk_count} chunks.",
        chunks_indexed=chunk_count,
        cache_hit=is_cached
    )

@router.get("", response_model=List[DocumentMetadata])
def list_documents():
    """Lists metadata for all stored sample documents."""
    os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
    doc_files = glob.glob(os.path.join(SAMPLE_DOCS_DIR, "*.*"))
    result = []

    for filepath in doc_files:
        filename = os.path.basename(filepath)
        stat = os.stat(filepath)
        chunks_count = sum(1 for chunk in vector_store.chunk_store.values() if chunk.filename == filename)
        result.append(DocumentMetadata(
            filename=filename,
            chunk_count=chunks_count,
            file_size_bytes=stat.st_size,
            last_modified=stat.st_mtime
        ))

    return result
