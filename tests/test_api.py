from pathlib import Path

from fastapi.testclient import TestClient

from api.app import build_app
from opencontext.index import LocalIndex
from opencontext.service import OpenContextService


def test_api_indexes_searches_and_answers(tmp_path: Path):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "activation.md").write_text(
        "# Activation\n## Definition\nActivation measures the first meaningful value."
    )
    service = OpenContextService(LocalIndex(tmp_path / "index.sqlite3"), knowledge)
    client = TestClient(build_app(service))
    assert client.get("/health").json()["status"] == "ok"
    assert client.post("/documents/index", json={"path": str(tmp_path)}).status_code == 400
    report = service.index(knowledge)
    assert report.total_chunks == 1
    search = client.post("/search", json={"query": "activation", "top_k": 1})
    assert search.status_code == 200
    assert search.json()["results"][0]["chunk"]["document_path"] == "activation.md"
    answer = client.post("/ask", json={"query": "activation", "top_k": 1})
    assert answer.json()["confidence"] == "grounded"
    assert answer.json()["sources"][0]["heading"] == "Definition"
