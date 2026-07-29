from fastapi import APIRouter, HTTPException
from backend.models.record import QueryRequest, QueryResponse
from backend.services.vector_store import vector_store

router = APIRouter(prefix="/api/search", tags=["search"])

@router.post("", response_model=QueryResponse)
def search_and_answer(request: QueryRequest):
    """Processes a user question, executes vector similarity search, and generates a cited answer."""
    question = request.question.strip() if request.question else ""
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Empty query error: Question text cannot be blank."
        )

    if not vector_store.chunk_store:
        raise HTTPException(
            status_code=404,
            detail="Missing documents error: No documents indexed in system. Please index documents first."
        )

    top_k = request.top_k or 3
    retrieved_results, latency_ms, is_cached = vector_store.search(question, top_k=top_k)
    
    if not retrieved_results:
        raise HTTPException(
            status_code=404,
            detail="No results found: No relevant document snippets matched your search query."
        )

    answer, sources = vector_store.generate_llm_answer(question, retrieved_results)

    return QueryResponse(
        answer=answer,
        sources=sources,
        latency_ms=round(latency_ms, 2),
        cache_hit=is_cached
    )
