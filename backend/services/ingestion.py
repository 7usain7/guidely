import os
import hashlib
from typing import List, Tuple
from backend.models.record import DocumentChunk

def compute_file_hash(filepath: str) -> str:
    """Computes SHA-256 hash of a file to detect changes for embedding caching."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def estimate_token_count(text: str) -> int:
    """Estimates token count (~4 characters per token average)."""
    return max(1, len(text) // 4)

def chunk_text(text: str, filename: str, target_tokens: int = 500) -> List[DocumentChunk]:
    """Splits document text into semantic paragraph chunks (~500 tokens each)."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[DocumentChunk] = []
    
    current_paragraphs = []
    current_length = 0
    chunk_index = 0

    for paragraph in paragraphs:
        para_tokens = estimate_token_count(paragraph)
        
        # If single paragraph is very large, split by line breaks
        if para_tokens > target_tokens * 1.5:
            lines = [line.strip() for line in paragraph.split("\n") if line.strip()]
            for line in lines:
                line_tokens = estimate_token_count(line)
                if current_length + line_tokens > target_tokens and current_paragraphs:
                    chunk_text_str = "\n".join(current_paragraphs)
                    chunk_id = f"{filename}#chunk-{chunk_index}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        filename=filename,
                        content=chunk_text_str,
                        chunk_index=chunk_index,
                        token_count=current_length
                    ))
                    chunk_index += 1
                    current_paragraphs = []
                    current_length = 0
                
                current_paragraphs.append(line)
                current_length += line_tokens
        else:
            if current_length + para_tokens > target_tokens and current_paragraphs:
                chunk_text_str = "\n\n".join(current_paragraphs)
                chunk_id = f"{filename}#chunk-{chunk_index}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    filename=filename,
                    content=chunk_text_str,
                    chunk_index=chunk_index,
                    token_count=current_length
                ))
                chunk_index += 1
                current_paragraphs = []
                current_length = 0
            
            current_paragraphs.append(paragraph)
            current_length += para_tokens

    # Append trailing chunk
    if current_paragraphs:
        chunk_text_str = "\n\n".join(current_paragraphs)
        chunk_id = f"{filename}#chunk-{chunk_index}"
        chunks.append(DocumentChunk(
            chunk_id=chunk_id,
            filename=filename,
            content=chunk_text_str,
            chunk_index=chunk_index,
            token_count=current_length
        ))

    return chunks

def load_and_chunk_document(filepath: str) -> Tuple[str, List[DocumentChunk], str]:
    """Loads a file, computes SHA-256 hash, and creates document chunks."""
    filename = os.path.basename(filepath)
    file_hash = compute_file_hash(filepath)
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    chunks = chunk_text(content, filename)
    return filename, chunks, file_hash
