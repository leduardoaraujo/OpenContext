from __future__ import annotations

import json
import math
import re
import sqlite3
from pathlib import Path

from opencontext.chunker import chunk_document
from opencontext.contracts import Chunk, Document, IndexReport, SearchResult
from opencontext.embeddings import HashEmbeddingProvider


def _cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True)) / (
        math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right)) or 1.0
    )


def _lexical_overlap(query: str, content: str) -> float:
    stopwords = {"a", "an", "and", "is", "the", "to", "what", "of", "for", "how"}
    query_terms = {
        term for term in re.findall(r"[a-z0-9]+", query.lower()) if term not in stopwords
    }
    content_terms = set(re.findall(r"[a-z0-9]+", content.lower()))
    return len(query_terms & content_terms) / len(query_terms) if query_terms else 0.0


class LocalIndex:
    def __init__(self, db_path: Path, embedder: HashEmbeddingProvider | None = None) -> None:
        self.db_path = Path(db_path)
        self.embedder = embedder or HashEmbeddingProvider()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS chunks "
                "(chunk_id TEXT PRIMARY KEY, data TEXT, vector TEXT)"
            )

    def build(self, documents: list[Document], rebuild: bool = False) -> IndexReport:
        with sqlite3.connect(self.db_path) as conn:
            if rebuild:
                conn.execute("DELETE FROM chunks")
            existing = {row[0] for row in conn.execute("SELECT chunk_id FROM chunks")}
            chunks = [chunk for doc in documents for chunk in chunk_document(doc)]
            new_chunks = [chunk for chunk in chunks if chunk.chunk_id not in existing]
            vectors = self.embedder.embed_texts([chunk.content for chunk in new_chunks])
            conn.executemany(
                "INSERT OR REPLACE INTO chunks(chunk_id, data, vector) VALUES (?, ?, ?)",
                [
                    (chunk.chunk_id, chunk.model_dump_json(), json.dumps(vector))
                    for chunk, vector in zip(new_chunks, vectors, strict=True)
                ],
            )
        return IndexReport(
            total_documents=len(documents),
            indexed_documents=len(documents) if new_chunks else 0,
            total_chunks=len(chunks),
            used_cache=not bool(new_chunks) and not rebuild,
        )

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
        return int(row[0]) if row else 0

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        query_vector = self.embedder.embed_query(query)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT data, vector FROM chunks").fetchall()
        ranked = []
        for data, vector_json in rows:
            chunk = Chunk.model_validate_json(data)
            score = _cosine(query_vector, json.loads(vector_json))
            score += 0.5 * _lexical_overlap(query, chunk.content)
            ranked.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                    stage="detail",
                )
            )
        return sorted(ranked, key=lambda result: result.score, reverse=True)[:top_k]
