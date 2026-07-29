import os
import sys
from fastapi.testclient import TestClient

# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app

def run_tests():
    client = TestClient(app)
    print("=== Running Guidely Backend & Metrics Integration Tests ===")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✓ /health endpoint passed")

    # 2. Index sample documents
    res = client.post("/api/documents/index-all")
    assert res.status_code == 200, f"Indexing failed: {res.text}"
    data = res.json()
    print(f"✓ Document Indexing passed: {data['total_documents']} docs, {data['total_chunks']} chunks indexed.")

    # 3. List documents
    res = client.get("/api/documents")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 5, f"Expected at least 5 docs, got {len(docs)}"
    print(f"✓ /api/documents listed {len(docs)} documents.")

    # 4. Search Queries (Retrieval & Citation Check)
    queries = [
        "What is the internet reimbursement allowance for remote employees?",
        "How do I reset my SSO password?",
        "What are the API design guidelines?",
        "How many days of PTO do employees get?",
        "What is the policy on password length and 1Password?"
    ]

    for q in queries:
        res = client.post("/api/search", json={"question": q, "top_k": 3})
        assert res.status_code == 200, f"Search failed for '{q}': {res.text}"
        payload = res.json()
        assert "answer" in payload and payload["answer"]
        assert len(payload["sources"]) > 0, "No sources cited!"
        print(f"✓ Query: '{q[:35]}...' -> Response in {payload['latency_ms']}ms, {len(payload['sources'])} sources cited.")

    # 5. Embedding cache hit test (Repeated query)
    res = client.post("/api/search", json={"question": queries[0], "top_k": 3})
    assert res.status_code == 200
    payload = res.json()
    assert payload["cache_hit"] is True, "Expected embedding cache hit on repeated query"
    print("✓ Embedding Cache Effectiveness: 100% cache hit on repeated query.")

    # 6. Failure handling tests
    # Empty query -> 400 Bad Request
    res = client.post("/api/search", json={"question": ""})
    assert res.status_code == 400
    print(f"✓ Failure Handling (Empty Query 400): {res.json()['detail']}")

    # 7. Metrics Endpoint Check
    res = client.get("/metrics")
    assert res.status_code == 200
    metrics = res.json()
    print(f"✓ /metrics endpoint: Total Queries={metrics['total_queries']}, Cache Hit Rate={metrics['cache_hit_rate']}%, Median Latency={metrics['median_latency_ms']}ms")

    print("\nALL BACKEND & METRICS INTEGRATION TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    run_tests()
