# Backend (Flask)

## Quickstart

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill keys
python -m app
```

The server listens on `http://localhost:8000` by default.

## Environment

- `GEMINI_API_KEY` — required for generation and image OCR
- `SUPABASE_URL` / `SUPABASE_ANON_KEY` — optional, enable cloud vector storage (pgvector)
- FAISS local index is used automatically as fallback.

## Endpoints

- `POST /api/upload` — multipart form with `file` or `files[]` (PDF, DOCX, TXT, images).
- `POST /api/ask` — JSON `{ "question": "...", "top_k": 5, "doc_id": "optional" }`

## Notes

- Chunk size: 1000 chars, overlap: 200 (as in your spec).
- Embeddings: `all-MiniLM-L6-v2` (384-dim).
- Retrieval: cosine similarity via Supabase pgvector or local FAISS fallback.
