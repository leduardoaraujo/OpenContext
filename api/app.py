from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from opencontext.config import OpenContextSettings
from opencontext.contracts import AskRequest, IndexRequest, SearchRequest
from opencontext.index import LocalIndex
from opencontext.service import OpenContextService


def build_app(service: OpenContextService | None = None) -> FastAPI:
    root = Path(__file__).resolve().parents[1]
    settings = OpenContextSettings.from_env(root)
    service = service or OpenContextService(LocalIndex(settings.db_path), settings.knowledge_root)
    app = FastAPI(
        title=settings.api_title,
        description="The open source retrieval engine behind GAV Insights.",
        version="0.1.0",
    )
    app.state.opencontext = service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "indexed_chunks": service.index_store.count()}

    @app.post("/documents/index")
    async def index_documents(payload: IndexRequest) -> dict[str, object]:
        try:
            report = service.index(root / payload.path, rebuild=payload.rebuild)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return report.model_dump()

    @app.post("/search")
    async def search(payload: SearchRequest) -> dict[str, object]:
        results = service.search(payload.query, payload.top_k)
        return {"results": [result.model_dump() for result in results]}

    @app.post("/ask")
    async def ask(payload: AskRequest) -> dict[str, object]:
        return service.ask(payload.query, payload.top_k).model_dump()

    return app


app = build_app()
