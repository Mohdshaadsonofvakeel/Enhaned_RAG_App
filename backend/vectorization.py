from typing import List, Tuple
from dataclasses import dataclass
import math

from sentence_transformers import SentenceTransformer
import numpy as np

from .config import settings

# Lazy-load model at module import (this can take time on first run)
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP

    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, settings.EMBEDDING_DIM), dtype=np.float32)
    model = get_model()
    embs = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embs, dtype=np.float32)

def embed_query(q: str) -> np.ndarray:
    return embed_texts([q])[0]
