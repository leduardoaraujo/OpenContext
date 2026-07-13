from __future__ import annotations

import os

from opencontext.contracts import SearchResult


def generate_grounded_answer(query: str, results: list[SearchResult]) -> str | None:
    """Use OpenAI only when explicitly configured; return None for retrieval-only mode."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    context = "\n\n".join(
        f"Source: {hit.chunk.document_path} · {hit.chunk.heading}\n{hit.chunk.content}"
        for hit in results
    )
    response = OpenAI(api_key=api_key).responses.create(
        model=os.getenv("OPENCONTEXT_OPENAI_MODEL", "gpt-4o-mini"),
        input=(
            "Answer only using the supplied context. If it is insufficient, say so.\n\n"
            f"Question: {query}\n\nContext:\n{context}"
        ),
    )
    return response.output_text.strip()
