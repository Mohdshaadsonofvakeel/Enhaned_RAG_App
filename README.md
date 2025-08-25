# Enhanced RAG App

End-to-end Retrieval-Augmented Generation web app: React frontend, Flask backend, embeddings with sentence-transformers, vector search via Supabase pgvector (or local FAISS fallback), and Gemini for response generation + image OCR.

## TL;DR

- Backend: `cd backend && pip install -r requirements.txt && cp .env.example .env && python -m app`
- Frontend: `cd frontend && npm install && cp .env.example .env && npm run dev`
- Supabase (optional): run SQL in `database/schema_supabase.sql` and set `SUPABASE_URL`, `SUPABASE_ANON_KEY` in backend `.env`.

## Features

- Document ingestion & text extraction (PDF, DOCX, TXT, images).
- Chunking (1000 chars) with 200-char overlap.  <!-- aligns with your guide -->
- Embeddings via `all-MiniLM-L6-v2` (384-dim).
- Vector store: Supabase pgvector or FAISS fallback.
- Semantic retrieval (cosine similarity) and Top-K (default 5).
- Prompt augmentation & answer with Gemini 1.5 Flash.

## Notes

- Provide `GEMINI_API_KEY` to enable generation and OCR.
- If Supabase is not configured, the app still works locally using FAISS.
- This project was built to reflect your RAG spec and workflow.

Generated: 2025-08-23 06:11:00Z
