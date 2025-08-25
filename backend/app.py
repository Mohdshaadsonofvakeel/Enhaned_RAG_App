import os
from uuid import uuid4
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from .config import settings
from .utils.logger import get_logger
from .text_extraction import extract_text_from_file, normalize_whitespace
from .vectorization import chunk_text, embed_texts, embed_query
from .retrieval import store_document, search_similar
from .ai_providers.gemini_provider import generate_answer

logger = get_logger()

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": settings.CORS_ORIGINS}})

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/upload")
    def upload():
        # support 'file' or 'files'
        files = request.files.getlist("files")
        if not files:
            f = request.files.get("file")
            if f:
                files = [f]
        results = []
        for f in files:
            filename = secure_filename(f.filename or f"upload-{uuid4().hex}")
            file_bytes = f.read()
            text, mime = extract_text_from_file(filename, file_bytes, use_gemini_vision=True)
            text = normalize_whitespace(text)
            chunks = chunk_text(text)
            embeddings = embed_texts(chunks)
            doc_id = store_document(filename, mime, chunks, embeddings)
            results.append({
                "filename": filename,
                "mime_type": mime,
                "doc_id": doc_id,
                "chunks": len(chunks)
            })
            logger.info(f"Processed {filename}: {len(chunks)} chunks -> doc_id={doc_id}")
        return jsonify({"ok": True, "items": results})

    @app.post("/api/ask")
    def ask():
        body = request.get_json(force=True, silent=True) or {}
        question = body.get("question", "").strip()
        top_k = int(body.get("top_k") or settings.TOP_K)
        doc_id = body.get("doc_id")  # optional filter to a specific document

        if not question:
            return jsonify({"ok": False, "error": "question is required"}), 400

        qvec = embed_query(question)
        matches = search_similar(qvec, top_k=top_k, doc_id=doc_id)
        chunks = [m.get("content", "") for m in matches]
        answer = generate_answer(chunks, question)

        return jsonify({
            "ok": True,
            "question": question,
            "top_k": top_k,
            "doc_id": doc_id,
            "answer": answer,
            "matches": matches
        })

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.PORT, debug=False)
