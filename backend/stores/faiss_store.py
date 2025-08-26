from typing import List, Dict, Any, Optional, Tuple
import os, json, uuid
import numpy as np
import faiss

from ..config import settings

def _paths():
    os.makedirs(settings.FAISS_DIR, exist_ok=True)
    return (
        os.path.join(settings.FAISS_DIR, "index.faiss"),
        os.path.join(settings.FAISS_DIR, "chunks.jsonl"),
    )

def _load_index(d: int) -> faiss.IndexFlatIP:
    index_path, _ = _paths()
    if os.path.exists(index_path):
        return faiss.read_index(index_path)
    index = faiss.IndexFlatIP(d)  # we store normalized vectors => cosine == inner product
    return index

def _load_chunks() -> List[Dict[str, Any]]:
    _, chunks_path = _paths()
    items = []
    if os.path.exists(chunks_path):
        with open(chunks_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    items.append(json.loads(line))
                except Exception:
                    pass
    return items

def _save_index(index: faiss.IndexFlatIP) -> None:
    index_path, _ = _paths()
    faiss.write_index(index, index_path)

def _append_chunks(new_items: List[Dict[str, Any]]) -> None:
    _, chunks_path = _paths()
    with open(chunks_path, "a", encoding="utf-8") as f:
        for item in new_items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def add_document(filename: str, mime_type: str, chunks: List[str], embeddings: np.ndarray) -> str:
    # Return a local doc_id for linking
    doc_id = str(uuid.uuid4())
    index = _load_index(embeddings.shape[1])
    # ensure normalized vectors (faiss IP works as cosine with normalized vectors)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12
    emb_norm = embeddings / norms
    index.add(emb_norm.astype("float32"))
    _save_index(index)

    # store chunks with doc_id and global position (id)
    items = []
    for i, ch in enumerate(chunks):
        items.append({"id": i, "doc_id": doc_id, "content": ch})
    _append_chunks(items)
    return doc_id

def search(query_embedding: np.ndarray, top_k: int = 5, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
    index = _load_index(query_embedding.shape[0])
    # normalize
    q = query_embedding / (np.linalg.norm(query_embedding) + 1e-12)
    D, I = index.search(q.reshape(1, -1).astype("float32"), top_k * 5)  # search more then filter
    items = _load_chunks()
    # map id -> item with optional doc filter
    results = []
    for idx, score in zip(I[0], D[0]):
        if idx < 0 or idx >= len(items):
            continue
        item = items[idx]
        if doc_id and item.get("doc_id") != doc_id:
            continue
        results.append({
            "id": idx,
            "doc_id": item.get("doc_id"),
            "content": item.get("content"),
            "similarity": float(score)
        })
        if len(results) >= top_k:
            break
    return results
