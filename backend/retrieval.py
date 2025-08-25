from typing import List, Dict, Any, Optional
import numpy as np

from .config import settings
from .stores import supabase_store, faiss_store

def supabase_available() -> bool:
    return supabase_store.available()

def store_document(filename: str, mime_type: str, chunks: List[str], embeddings: np.ndarray) -> str:
    if supabase_available():
        doc_id = supabase_store.create_document(filename, mime_type)
        supabase_store.insert_chunks(doc_id, chunks, embeddings)
        return doc_id
    else:
        # local FAISS fallback
        doc_id = faiss_store.add_document(filename, mime_type, chunks, embeddings)
        return doc_id

def search_similar(query_embedding: np.ndarray, top_k: int, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if supabase_available():
        return supabase_store.similarity_search(query_embedding, top_k=top_k, doc_id=doc_id)
    else:
        return faiss_store.search(query_embedding, top_k=top_k, doc_id=doc_id)
