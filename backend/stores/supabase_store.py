from typing import List, Optional, Dict, Any
import uuid
import numpy as np
from supabase import create_client, Client

from ..config import settings

_client: Optional[Client] = None

def get_client() -> Optional[Client]:
    global _client
    if _client is None and settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _client

def available() -> bool:
    return get_client() is not None

def create_document(filename: str, mime_type: str) -> str:
    client = get_client()
    if not client:
        raise RuntimeError("Supabase not configured")
    doc_id = str(uuid.uuid4())
    client.table("documents").insert({
        "id": doc_id,
        "filename": filename,
        "mime_type": mime_type,
    }).execute()
    return doc_id

def insert_chunks(doc_id: str, chunks: List[str], embeddings: np.ndarray) -> None:
    client = get_client()
    if not client:
        raise RuntimeError("Supabase not configured")
    rows = []
    for ch, emb in zip(chunks, embeddings):
        rows.append({
            "doc_id": doc_id,
            "content": ch,
            "embedding": emb.tolist()
        })
    # insert in batches to avoid payload limits
    batch_size = 500
    for i in range(0, len(rows), batch_size):
        client.table("chunks").insert(rows[i:i+batch_size]).execute()

def similarity_search(query_embedding: np.ndarray, top_k: int = 5, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
    client = get_client()
    if not client:
        raise RuntimeError("Supabase not configured")

    payload = {
        "query_embedding": query_embedding.tolist(),
        "match_count": top_k
    }
    if doc_id:
        payload["filter_doc"] = doc_id
    # call RPC function
    resp = client.rpc("match_chunks", payload).execute()
    data = resp.data or []
    # expected fields: id, doc_id, content, similarity
    return data
