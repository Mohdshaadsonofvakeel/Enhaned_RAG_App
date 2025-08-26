from typing import List, Optional
import google.generativeai as genai
import os
from ..config import settings

def _configure():
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_answer(chunks: List[str], question: str) -> str:
    """Generate an answer using Gemini with the retrieved chunks as context."""
    if not settings.GEMINI_API_KEY:
        return "Gemini API key not configured. Set GEMINI_API_KEY to enable generation."
    _configure()
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    context = "\n\n".join(f"[Chunk {i+1}] {c}" for i, c in enumerate(chunks))
    prompt = f"""You are a helpful assistant. Answer the user's question *only* using the provided context.
If the answer is not contained in the context, say you don't have enough information.

Context:
{context}

Question: {question}
Answer:"""
    resp = model.generate_content(prompt)
    return getattr(resp, "text", "").strip() or "No response generated."

def ocr_image_with_gemini(image_bytes: bytes) -> str:
    if not settings.GEMINI_API_KEY:
        return ""
    _configure()
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    # Provide the image and a short OCR instruction
    resp = model.generate_content([
        {"mime_type": "image/png", "data": image_bytes},
        "Extract all textual content from this image. Return plain text only."
    ])
    return getattr(resp, "text", "") or ""
