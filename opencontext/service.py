from __future__ import annotations

from pathlib import Path

from opencontext.contracts import AnswerResponse, IndexReport, SearchResult
from opencontext.index import LocalIndex
from opencontext.llm import generate_grounded_answer
from opencontext.loader import load_documents


class OpenContextService:
    def __init__(self, index: LocalIndex, knowledge_root: Path) -> None:
        self.index_store = index
        self.knowledge_root = Path(knowledge_root).resolve()

    def index(self, root: Path | None = None, rebuild: bool = False) -> IndexReport:
        knowledge = Path(root or self.knowledge_root).resolve()
        if not knowledge.is_relative_to(self.knowledge_root):
            raise ValueError("Knowledge path must stay inside the configured knowledge root")
        return self.index_store.build(load_documents(knowledge), rebuild=rebuild)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        return self.index_store.search(query, top_k=top_k)

    def ask(self, query: str, top_k: int = 5) -> AnswerResponse:
        results = self.search(query, top_k=top_k)
        if not results or results[0].score <= 0:
            return AnswerResponse(
                answer="Insufficient context to answer this question.",
                confidence="insufficient",
            )
        grounded_results = [result for result in results if result.score > 0]
        sources = [
            {
                "path": hit.chunk.document_path,
                "heading": hit.chunk.heading,
                "score": hit.score,
                "excerpt": hit.chunk.content,
            }
            for hit in grounded_results[:top_k]
        ]
        answer = generate_grounded_answer(query, grounded_results) or "\n\n".join(
            f"[{source['path']} · {source['heading']}]\n{source['excerpt']}"
            for source in sources
        )
        return AnswerResponse(answer=answer, confidence="grounded", sources=sources)
