from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentChunk(BaseModel):
    """Represents a text chunk created from a document."""
    chunk_id: str
    filename: str
    content: str
    chunk_index: int
    token_count: int
    metadata: Optional[Dict[str, Any]] = {}

class QueryRequest(BaseModel):
    """Payload sent by user for Q&A vector search."""
    question: str
    top_k: Optional[int] = Field(default=3, ge=1, le=10)

class SourceCitation(BaseModel):
    """Represents a cited source snippet backing an LLM answer."""
    filename: str
    chunk_id: str
    snippet: str
    relevance_score: float

class QueryResponse(BaseModel):
    """Payload returned after running RAG vector search."""
    answer: str
    sources: List[SourceCitation]
    latency_ms: float
    cache_hit: bool

class DocumentMetadata(BaseModel):
    """Metadata summary for a stored document."""
    filename: str
    chunk_count: int
    file_size_bytes: int
    last_modified: float

class DocumentUploadResponse(BaseModel):
    """Response returned upon uploading or indexing a file."""
    filename: str
    message: str
    chunks_indexed: int
    cache_hit: bool

class SystemMetrics(BaseModel):
    """System performance metrics for monitoring latency and cache effectiveness."""
    total_documents: int
    total_chunks: int
    total_queries: int
    cache_hit_rate: float
    median_latency_ms: float
    p95_latency_ms: float
