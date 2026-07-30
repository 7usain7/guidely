# Guidely - Internal Workplace AI Knowledge Assistant & RAG Engine

Guidely is an internal workplace knowledge assistant built with a **React (Vite)** chatbot frontend and a **FastAPI (Python)** backend. It ingests company documentation (policies, engineering guides, IT FAQs, employee handbooks), converts them into vector embeddings via the **Google Gemini API**, indexes vectors with **FAISS**, and generates fast, accurate, natural-language answers with cited document source snippets using **Groq (Llama 3.3)**.

---

## Features

- **Clean Workplace Chatbot Interface:** Slack/ChatGPT-style message bubble layout with rendered Markdown formatting, quick question prompt pills, top-$k$ context selector, and interactive source citation cards.
- **100% Remote API Architecture:**
  - **Vector Embeddings API:** Google Gemini API (`gemini-embedding-001`).
  - **LLM Generation API:** Groq API (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant` at 500+ tokens/sec).
- **FAISS Vector Persistence & 100% Embedding Cache:**
  - Saves binary vector index files to disk at `backend/data/faiss_index`.
  - SHA-256 text hashing in `embedding_cache.json` guarantees $100\%$ cache hit effectiveness on unchanged files.
- **Dual-View User Interface:**
  - **Chat Assistant:** Interactive Q&A chat stream, quick suggestion pills, top-$k$ depth selector, and source citations.
  - **Doc Management & Metrics Admin:** Drag-and-drop `.txt`/`.md` document uploader, live manual re-indexing trigger with dynamic disk-purge sync, document inventory table, and auto-logged metrics.
- **Automated Metrics & Graceful Failure Handling:**
  - Tracks median and p95 latency, total queries, and cache hit percentages.
  - Returns clean HTTP 400 for empty queries and HTTP 404 for missing or unindexed documents.

---

## Repository Architecture

```text
guidely/
├── frontend/             # Vite + React Workplace Chat UI
│   ├── src/
│   │   ├── components/   # Navbar.jsx
│   │   ├── pages/        # ChatPage.jsx, AdminPage.jsx
│   │   ├── App.jsx
│   │   └── index.css     # Design system & Markdown typography
│   └── vite.config.js    # API proxy for /api and /metrics
│
├── backend/              # Python FastAPI Application
│   ├── main.py           # Entrypoint & startup auto-indexing
│   ├── models/           # Pydantic schemas (record.py)
│   ├── routes/           # REST endpoints (documents.py, search.py, metrics.py)
│   ├── services/         # Vector DB & Ingestion (vector_store.py, ingestion.py)
│   └── data/
│       ├── faiss_index   # FAISS binary vector index
│       └── sample-docs/  # Real-world corporate dataset
│
├── requirements.txt      # Python dependencies (fastapi, google-genai, groq, faiss-cpu)
├── .env.example          # Environment configuration template
└── README.md
```

---

## Setup & Installation

### 1. Environment Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
GEMINI_API_KEY=AIzaSyYourGeminiKeyHere...
GROQ_API_KEY=gsk_YourGroqKeyHere...
PORT=8000
HOST=0.0.0.0
VECTOR_DB_PATH=backend/data/faiss_index
```

### 2. Run Backend Server

```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

- Health Check: `http://localhost:8000/health`
- Metrics Endpoint: `http://localhost:8000/metrics`

### 3. Run Frontend Chatbot App

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Real-World Corporate Dataset

The `backend/data/sample-docs/` directory includes 5 real-world corporate policy and technical files:

1. `company_benefits_and_perks.txt` — Healthcare, dental, 401(k) matching, PTO, wellness & L&D stipends.
2. `it_security_and_compliance.txt` — Password standards, 1Password, YubiKey MFA, device encryption, data classification.
3. `remote_work_and_travel_policy.txt` — Core hours, $1,000 setup stipend, $70 internet reimbursement, travel per diems.
4. `engineering_best_practices.txt` — Git branching, PR approvals, REST conventions, SEV-1/2/3 incident response.
5. `employee_onboarding_faq.txt` — First week checklist, AccessPortal software requests, WireGuard VPN configuration.

## License

This project is proprietary. The code is publicly visible for portfolio and viewing purposes only. No unauthorized copying, modification, or distribution is permitted. See [License](LICENSE) for details.
