"""Simple local RAG utilities with sentence-transformers cosine similarity.

No external vector database is used. Documents are loaded from /context,
chunked in-memory, embedded locally, and retrieved at runtime.
"""

import os
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings

# Set HF token if available to avoid unauthenticated warnings
if settings.hf_token:
    os.environ["HF_TOKEN"] = settings.hf_token


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Splits text into overlapping chunks for better retrieval granularity."""
    if not text.strip():
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def load_context_chunks(context_dir: str) -> List[str]:
    """Reads all .txt files in the context folder and returns chunked content."""
    chunks: List[str] = []
    for file_path in sorted(Path(context_dir).glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")
        chunks.extend(chunk_text(text))
    return chunks


class LocalRetriever:
    """In-memory cosine similarity retriever based on sentence-transformers."""

    def __init__(self, context_chunks: List[str]) -> None:
        self.context_chunks = context_chunks
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = (
            self.model.encode(context_chunks, normalize_embeddings=True)
            if context_chunks
            else np.array([])
        )

    def retrieve(self, query: str, top_k: int = 4) -> List[Tuple[str, float]]:
        """Returns the top-k chunks and similarity scores for a query."""
        if len(self.context_chunks) == 0:
            return []
        query_emb = self.model.encode([query], normalize_embeddings=True)[0]
        # Cosine similarity is dot product because vectors are normalized.
        scores = np.dot(self.embeddings, query_emb)
        idx = np.argsort(scores)[::-1][:top_k]
        return [(self.context_chunks[i], float(scores[i])) for i in idx]
