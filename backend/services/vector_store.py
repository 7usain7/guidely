import os
import json
import numpy as np
import time
import math
import hashlib
from typing import List, Dict, Tuple, Optional, Any
from backend.models.record import DocumentChunk, SourceCitation

# Persistent embedding cache file path
CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
CACHE_FILE = os.path.join(CACHE_DIR, "embedding_cache.json")

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
        """Saves current embedding cache to JSON file."""
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f)

    def _generate_embedding(self, text: str) -> Tuple[List[float], bool]:
        """Generates embedding for text with 100% cache hit lookup and local fallback."""
        text_hash = hashlib_str(text)
        if text_hash in self.cache:
            return self.cache[text_hash], True  # Cache hit!

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                vec = response.data[0].embedding
                self.cache[text_hash] = vec
                self._save_cache()
                return vec, False
            except Exception as e:
                print(f"[VectorStore] OpenAI embedding fallback due to: {e}")

        # Deterministic lightweight semantic vector embedding (fallback)
        words = text.lower().split()
        dim = 128
        vec = [0.0] * dim
        for w in words:
            h = int(hashlib_str(w), 16)
            idx = h % dim
            val = ((h >> 8) % 100) / 100.0
            vec[idx] += val
        
        # Normalize vector to unit length
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        norm_vec = [x / norm for x in vec]
        
        self.cache[text_hash] = norm_vec
        self._save_cache()
        return norm_vec, False

    def index_document(self, filename: str, chunks: List[DocumentChunk], file_hash: str) -> Tuple[int, bool]:
        """Indexes document chunks into vector store. Returns (chunks_indexed, is_full_cache_hit)."""
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

        return len(chunks), all_cached

    def search(self, query: str, top_k: int = 3) -> Tuple[List[Tuple[DocumentChunk, float]], float, bool]:
        """Executes vector similarity search for a query. Returns top-k (chunk, score), latency_ms, is_cached."""
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
        """Generates answer using LLM or structured RAG synthesizer with source citations."""
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

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                joined_context = "\n\n".join(context_snippets)
                prompt = (
                    "You are Guidely, an internal company knowledge assistant. "
                    "Answer the user's question directly and concisely based strictly on the provided context passages. "
                    "Cite your sources where appropriate.\n\n"
                    f"Context:\n{joined_context}\n\n"
                    f"Question: {query}\nAnswer:"
                )
                res = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                return res.choices[0].message.content.strip(), citations
            except Exception as e:
                print(f"[VectorStore] LLM call fallback due to: {e}")

        # Smart fallback RAG synthesis
        top_chunk = retrieved_results[0][0]
        summary_answer = (
            f"Based on **{top_chunk.filename}**, here is the relevant information regarding your query:\n\n"
            f"> {top_chunk.content}\n\n"
            f"For further details, please review the complete source document referenced below."
        )
        return summary_answer, citations

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
