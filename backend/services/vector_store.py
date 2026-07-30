import os
import json
import numpy as np
import time
import hashlib
import faiss
from typing import List, Dict, Tuple, Optional, Any
from backend.models.record import DocumentChunk, SourceCitation

# Persistent embedding cache and FAISS index file paths
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
CACHE_FILE = os.path.join(CACHE_DIR, "embedding_cache.json")
FAISS_FILE = os.getenv("VECTOR_DB_PATH", os.path.join(CACHE_DIR, "faiss_index"))

def hashlib_str(s: str) -> str:
    """Computes SHA-256 hash string for embedding caching lookup."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

class VectorStore:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.chunk_store: Dict[str, DocumentChunk] = {} # chunk_id -> DocumentChunk
        self.doc_hashes: Dict[str, str] = {}            # filename -> sha256_hash
        self.embeddings: Dict[str, List[float]] = {}    # chunk_id -> vector
        self.cache: Dict[str, List[float]] = self._load_cache() # hash(text) -> vector
        
        # Metrics trackers
        self.total_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.latencies: List[float] = []

    def _load_cache(self) -> Dict[str, List[float]]:
        """Loads persistent embedding cache from JSON file."""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        """Saves current embedding cache and FAISS index file to disk."""
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f)
        self._save_faiss_index()

    def _save_faiss_index(self):
        """Saves current vectors into FAISS index file on disk at VECTOR_DB_PATH."""
        if not self.embeddings:
            return
        try:
            dim = len(next(iter(self.embeddings.values())))
            matrix = np.array(list(self.embeddings.values()), dtype=np.float32)
            faiss.normalize_L2(matrix)
            index = faiss.IndexFlatIP(dim)
            index.add(matrix)
            faiss.write_index(index, FAISS_FILE)
        except Exception as e:
            print(f"[VectorStore] FAISS index write warning: {e}")

    def _generate_embedding(self, text: str) -> Tuple[List[float], bool]:
        """Generates embedding for text via Google Gemini API with 100% SHA-256 cache hit lookup."""
        text_hash = hashlib_str(text)
        if text_hash in self.cache:
            return self.cache[text_hash], True  # Cache hit!

        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            raise RuntimeError("GEMINI_API_KEY Missing: Please configure GEMINI_API_KEY in your .env file for vector embeddings.")

        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            res = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
            )
            vec = list(res.embeddings[0].values)
            self.cache[text_hash] = vec
            self._save_cache()
            return vec, False
        except Exception as e:
            raise RuntimeError(f"Google Gemini API embedding error: {e}")

    def index_document(self, filename: str, chunks: List[DocumentChunk], file_hash: str) -> Tuple[int, bool]:
        """Indexes document chunks into vector store and saves FAISS index to disk. Returns (chunks_indexed, is_full_cache_hit)."""
        # Remove existing chunks for this file if updated
        existing_chunks = [cid for cid, chunk in self.chunk_store.items() if chunk.filename == filename]
        for cid in existing_chunks:
            del self.chunk_store[cid]
            if cid in self.embeddings:
                del self.embeddings[cid]

        self.doc_hashes[filename] = file_hash
        all_cached = True

        for chunk in chunks:
            vec, was_cached = self._generate_embedding(chunk.content)
            self.chunk_store[chunk.chunk_id] = chunk
            self.embeddings[chunk.chunk_id] = vec
            if not was_cached:
                all_cached = False

        self._save_faiss_index()
        return len(chunks), all_cached

    def search(self, query: str, top_k: int = 3) -> Tuple[List[Tuple[DocumentChunk, float]], float, bool]:
        """Executes FAISS / Cosine vector similarity search for a query. Returns top-k (chunk, score), latency_ms, is_cached."""
        start_time = time.time()
        self.total_queries += 1
        
        query_vec, query_was_cached = self._generate_embedding(query)
        if query_was_cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if not self.embeddings:
            latency_ms = (time.time() - start_time) * 1000
            self.latencies.append(latency_ms)
            return [], latency_ms, query_was_cached

        # Cosine similarity calculation
        scores: List[Tuple[DocumentChunk, float]] = []
        q_norm = np.linalg.norm(query_vec) or 1.0

        for chunk_id, chunk_vec in self.embeddings.items():
            # Dimensionality check: re-embed via API if vector dimensions mismatch
            if len(chunk_vec) != len(query_vec):
                chunk = self.chunk_store[chunk_id]
                new_vec, _ = self._generate_embedding(chunk.content)
                self.embeddings[chunk_id] = new_vec
                chunk_vec = new_vec

            dot_product = np.dot(query_vec, chunk_vec)
            c_norm = np.linalg.norm(chunk_vec) or 1.0
            similarity = float(dot_product / (q_norm * c_norm))
            chunk = self.chunk_store[chunk_id]
            scores.append((chunk, similarity))

        # Sort by similarity score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        results = scores[:top_k]

        latency_ms = (time.time() - start_time) * 1000
        self.latencies.append(latency_ms)

        return results, latency_ms, query_was_cached

    def generate_llm_answer(self, query: str, retrieved_results: List[Tuple[DocumentChunk, float]]) -> Tuple[str, List[SourceCitation]]:
        """Generates answer strictly via Groq API (Llama 3.3 / Llama 3.1) with source citations."""
        if not retrieved_results:
            return "I couldn't find any relevant documents answering your query in the internal system.", []

        citations: List[SourceCitation] = []
        context_snippets = []

        for chunk, score in retrieved_results:
            snippet = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            citations.append(SourceCitation(
                filename=chunk.filename,
                chunk_id=chunk.chunk_id,
                snippet=snippet,
                relevance_score=round(score, 4)
            ))
            context_snippets.append(f"Source [{chunk.filename}]:\n{chunk.content}")

        joined_context = "\n\n".join(context_snippets)
        prompt = (
            "You are Guidely, an internal company knowledge assistant. "
            "Answer the user's question directly and concisely based strictly on the provided context passages. "
            "Cite your sources where appropriate.\n\n"
            f"Context:\n{joined_context}\n\n"
            f"Question: {query}\nAnswer:"
        )

        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key or groq_key == "your_groq_api_key_here":
            raise RuntimeError("GROQ_API_KEY Missing: Please configure GROQ_API_KEY in your .env file.")

        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            
            # Ultra-fast Groq Llama 3 models
            groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192"]
            for model_name in groq_models:
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )
                    content = response.choices[0].message.content
                    if content:
                        return content.strip(), citations
                except Exception as model_err:
                    print(f"[VectorStore] Groq model '{model_name}' attempt error: {model_err}")
            
            raise RuntimeError("All Groq models failed to generate response.")
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Calculates system metrics including median/p95 latency and cache hit percentages."""
        total_queries = self.total_queries or 1
        hit_rate = round((self.cache_hits / total_queries) * 100, 2)
        
        if self.latencies:
            sorted_lat = sorted(self.latencies)
            median_lat = round(float(np.median(sorted_lat)), 2)
            p95_lat = round(float(np.percentile(sorted_lat, 95)), 2)
        else:
            median_lat = 0.0
            p95_lat = 0.0

        filenames = set(chunk.filename for chunk in self.chunk_store.values())
        return {
            "total_documents": len(filenames),
            "total_chunks": len(self.chunk_store),
            "total_queries": self.total_queries,
            "cache_hit_rate": hit_rate,
            "median_latency_ms": median_lat,
            "p95_latency_ms": p95_lat
        }

# Global VectorStore Singleton Instance
vector_store = VectorStore()
