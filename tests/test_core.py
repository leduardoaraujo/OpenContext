from pathlib import Path

from opencontext.chunker import chunk_document
from opencontext.contracts import Document
from opencontext.embeddings import HashEmbeddingProvider
from opencontext.index import LocalIndex
from opencontext.loader import load_documents
from opencontext.service import OpenContextService


def test_loader_and_chunker_keep_frontmatter_and_heading(tmp_path: Path):
    root = tmp_path / "knowledge"
    root.mkdir()
    content = "---\ntags: [activation]\n---\n# Guide\n## North Star\nActivation is a useful metric."
    (root / "guide.md").write_text(content, encoding="utf-8")
    document = load_documents(root)[0]
    chunks = chunk_document(document)
    assert document.metadata["tags"] == ["activation"]
    assert chunks[0].heading == "North Star"
    assert chunks[0].metadata["heading_path"] == "Guide > North Star"


def test_hash_embeddings_are_deterministic_and_search_is_ranked(tmp_path: Path):
    provider = HashEmbeddingProvider(32)
    assert provider.embed_query("activation") == provider.embed_query("activation")
    index = LocalIndex(tmp_path / "index.sqlite3", provider)
    docs = [Document(relative_path="a.md", title="A", body="# A\nActivation measures first value.")]
    assert index.build(docs).total_chunks == 1
    assert index.search("activation", top_k=1)[0].score > 0
    assert index.search("activation", top_k=1)[0].chunk.document_path == "a.md"
    assert index.build(docs).used_cache is True


def test_service_stays_retrieval_only_without_api_key(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "guide.md").write_text("# Guide\n## Definition\nActivation is first value.")
    index = LocalIndex(tmp_path / "index.sqlite3")
    service = OpenContextService(index, knowledge)
    service.index()
    assert service.ask("activation").confidence == "grounded"
