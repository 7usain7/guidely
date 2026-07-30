from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from backend.routes.documents import router as documents_router, index_all_sample_documents
from backend.routes.search import router as search_router
from backend.routes.metrics import router as metrics_router

app = FastAPI(
    title="Guidely Knowledge Assistant API",
    description="RAG-powered Q&A engine over internal company documentation",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include sub-routers
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(metrics_router)

@app.on_event("startup")
def startup_event():
    """Auto-index sample docs on application startup."""
    try:
        res = index_all_sample_documents()
        print(f"[Guidely API] Startup indexing complete: {res.get('message')}")
    except Exception as e:
        print(f"[Guidely API] Startup indexing warning: {e}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Guidely Knowledge Assistant API",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
