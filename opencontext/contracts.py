from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Document(BaseModel):
    relative_path: str
    title: str
    body: str
    metadata: dict[str, object] = Field(default_factory=dict)


class Chunk(BaseModel):
    chunk_id: str
    document_path: str
    title: str
    heading: str
    content: str
    metadata: dict[str, object] = Field(default_factory=dict)


class SearchResult(BaseModel):
    chunk: Chunk
    score: float
    stage: str

    @field_validator("score")
    @classmethod
    def validate_score(cls, value: float) -> float:
        return max(-1.0, min(1.0, value))


class IndexReport(BaseModel):
    total_documents: int
    indexed_documents: int
    total_chunks: int
    used_cache: bool


class Source(BaseModel):
    path: str
    heading: str
    score: float
    excerpt: str


class AnswerResponse(BaseModel):
    answer: str
    confidence: str
    sources: list[Source] = Field(default_factory=list)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class IndexRequest(BaseModel):
    path: str = "examples/knowledge"
    rebuild: bool = False


class AskRequest(SearchRequest):
    pass
