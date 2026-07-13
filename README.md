# OpenContext

## The open source engine behind GAV Insights

OpenContext is the retrieval and context engine that makes GAV Insights possible. It is the reusable, open source foundation responsible for loading documents, chunking content, generating embeddings, ranking evidence, and exposing grounded context through an API.

GAV Insights adds business-specific orchestration, Power BI/Fabric integrations, and the executive experience on top of this kind of engine. OpenContext is intentionally independent: it contains no proprietary connectors, credentials, customer data, or GAV business rules.

Grounded retrieval for explainable AI applications.

OpenContext is a small, dependency-light RAG project for Markdown knowledge bases. It includes a Python library, a FastAPI service, and a React demo UI. The default mode is retrieval-only: every answer is assembled from indexed evidence and includes its source path, heading, excerpt, and score.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
\.venv\Scripts\python.exe -m uvicorn serve:app --reload
```

In another terminal:

```powershell
cd ui
npm install
npm run dev
```

Open `http://127.0.0.1:5173`, index the example corpus through the API, or run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/documents/index -Method Post -ContentType 'application/json' -Body '{"path":"examples/knowledge"}'
Invoke-RestMethod http://127.0.0.1:8000/ask -Method Post -ContentType 'application/json' -Body '{"query":"What is activation?"}'
```

## Design

Markdown files are parsed into documents, split into heading-aware chunks, embedded with a deterministic local hashing provider, persisted in SQLite, and ranked by cosine similarity. The API exposes the same service through `/health`, `/documents/index`, `/search`, and `/ask`.

The hashing provider keeps the demo self-contained. The `EmbeddingProvider` shape in `opencontext/embeddings.py` is intentionally small so a sentence-transformer or hosted provider can be added without changing the retriever contract.

## Development

```powershell
python -m pytest -q
python -m ruff check opencontext api serve.py tests
cd ui
npm run build
```

The corpus is synthetic and exists only to demonstrate provenance. Do not commit secrets, private documents, local indexes, or customer data.

## License

MIT. See [LICENSE](LICENSE).
