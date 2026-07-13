# OpenContext Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an independent open source RAG portfolio project with a Python library, FastAPI service, and React/Vite demo UI.

**Architecture:** A small `opencontext` package owns Markdown loading, chunking, deterministic local embeddings, SQLite persistence, retrieval, and optional answer generation. FastAPI exposes that service through `/health`, `/documents/index`, `/search`, and `/ask`; React/Vite renders a single search-and-evidence workflow.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, Uvicorn, PyYAML, NumPy-free deterministic hashing embeddings, SQLite, React 18, Vite 5, pytest, ruff.

## Global Constraints

- The project name is `OpenContext` everywhere in package metadata, docs, API title, and UI copy.
- No Power BI, Fabric, PostgreSQL, MCP, Cosmos DB, authentication, session, feedback, or GAV-specific code/data may be copied.
- The API must run in retrieval-only mode without external credentials.
- Every `/ask` response must expose evidence or explicitly report insufficient context.
- `.env`, caches, local databases, build artifacts, and credentials must be ignored.
- All implementation changes must be verified with focused tests before moving to the next task.

---

### Task 1: Create the Python package and public contracts

**Files:**
- Create: `opencontext/__init__.py`
- Create: `opencontext/contracts.py`
- Create: `opencontext/config.py`
- Modify: `pyproject.toml`
- Test: `tests/test_contracts.py`

**Interfaces:**
- `Document(relative_path: str, title: str, body: str, metadata: dict[str, object])`
- `Chunk(chunk_id: str, document_path: str, title: str, heading: str, content: str, metadata: dict[str, object])`
- `SearchResult(chunk: Chunk, score: float, stage: str)`
- `IndexReport(total_documents: int, indexed_documents: int, total_chunks: int, used_cache: bool)`
- `OpenContextSettings.from_env() -> OpenContextSettings`

- [ ] Write tests that validate Pydantic serialization, score bounds, and safe default paths.
- [ ] Run `python -m pytest tests/test_contracts.py -q` and confirm the new tests fail before implementation.
- [ ] Implement the contracts and settings with defaults rooted at `examples/knowledge` and `.opencontext/index.sqlite3`.
- [ ] Run the focused test and confirm it passes.
- [ ] Commit with `git add opencontext pyproject.toml tests/test_contracts.py; git commit -m "feat: add OpenContext contracts and settings"`.

### Task 2: Implement Markdown loading and heading-aware chunking

**Files:**
- Create: `opencontext/loader.py`
- Create: `opencontext/chunker.py`
- Test: `tests/test_loader.py`
- Test: `tests/test_chunker.py`
- Create: `tests/fixtures/knowledge/overview.md`

**Interfaces:**
- `load_documents(root: Path) -> list[Document]`
- `chunk_document(document: Document, max_chars: int = 1200) -> list[Chunk]`

- [ ] Add fixture Markdown with YAML frontmatter, H1, H2, and H3 headings.
- [ ] Add failing tests for UTF-8 loading, metadata normalization, ignored non-Markdown files, heading paths, and deterministic chunk IDs.
- [ ] Run `python -m pytest tests/test_loader.py tests/test_chunker.py -q` and verify failure.
- [ ] Implement frontmatter parsing with `yaml.safe_load`, heading-aware segmentation, and character-boundary splitting for oversized sections.
- [ ] Run both test modules and confirm they pass.
- [ ] Commit with `git add opencontext tests; git commit -m "feat: add markdown loading and chunking"`.

### Task 3: Add deterministic embeddings and SQLite index/retriever

**Files:**
- Create: `opencontext/embeddings.py`
- Create: `opencontext/index.py`
- Create: `opencontext/retriever.py`
- Test: `tests/test_retriever.py`

**Interfaces:**
- `EmbeddingProvider.embed_texts(texts: list[str]) -> list[list[float]]`
- `HashEmbeddingProvider(dimension: int = 256)` implementing deterministic normalized vectors.
- `LocalIndex(db_path: Path, embedder: EmbeddingProvider)`
- `LocalIndex.build(documents: list[Document], rebuild: bool = False) -> IndexReport`
- `LocalIndex.search(query: str, top_k: int = 5) -> list[SearchResult]`

- [ ] Add tests for deterministic vectors, empty indexes, ranked search, and incremental cache behavior.
- [ ] Run `python -m pytest tests/test_retriever.py -q` and confirm failure.
- [ ] Implement SQLite tables for documents/chunks, JSON vectors, cosine similarity, and a two-stage ranking path that prioritizes index chunks before detailed chunks.
- [ ] Run the focused tests and confirm they pass.
- [ ] Commit with `git add opencontext tests; git commit -m "feat: add local indexed retrieval"`.

### Task 4: Add the service layer and retrieval-only answer composer

**Files:**
- Create: `opencontext/service.py`
- Test: `tests/test_service.py`

**Interfaces:**
- `OpenContextService.index(root: Path, rebuild: bool = False) -> IndexReport`
- `OpenContextService.search(query: str, top_k: int = 5) -> list[SearchResult]`
- `OpenContextService.ask(query: str, top_k: int = 5) -> AnswerResponse`

- [ ] Add tests for successful evidence-backed answers and explicit insufficient-context answers.
- [ ] Run `python -m pytest tests/test_service.py -q` and confirm failure.
- [ ] Implement a deterministic retrieval-only composer that summarizes matched evidence as labeled excerpts and includes source paths, headings, scores, and a confidence status.
- [ ] Run the focused tests and confirm they pass.
- [ ] Commit with `git add opencontext tests; git commit -m "feat: add grounded service facade"`.

### Task 5: Expose the FastAPI application

**Files:**
- Create: `api/__init__.py`
- Create: `api/app.py`
- Create: `serve.py`
- Test: `tests/test_api.py`

**Interfaces:**
- `build_app(service: OpenContextService | None = None) -> FastAPI`
- `GET /health`
- `POST /documents/index` with `{ "path": "examples/knowledge", "rebuild": false }`
- `POST /search` with `{ "query": "...", "top_k": 5 }`
- `POST /ask` with `{ "query": "...", "top_k": 5 }`

- [ ] Add HTTP tests for health, search, indexing, validation errors, and ask response evidence.
- [ ] Run `python -m pytest tests/test_api.py -q` and confirm failure.
- [ ] Implement CORS for local UI origins, safe path resolution constrained to the repository knowledge root, and JSON responses backed by the service contracts.
- [ ] Run the focused API tests and confirm they pass.
- [ ] Commit with `git add api serve.py tests; git commit -m "feat: expose OpenContext FastAPI"`.

### Task 6: Add neutral example corpus and project documentation

**Files:**
- Create: `examples/knowledge/index.md`
- Create: `examples/knowledge/retention.md`
- Create: `examples/knowledge/activation.md`
- Create: `README.md`
- Create: `LICENSE`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `CONTRIBUTING.md`
- Create: `CODE_OF_CONDUCT.md`
- Create: `SECURITY.md`
- Create: `docs/architecture.md`
- Create: `docs/quickstart.md`

- [ ] Write the example corpus with synthetic product analytics definitions and no company-specific references.
- [ ] Document installation, `python -m uvicorn serve:app --reload`, curl examples, UI startup, retrieval-only behavior, and extension points.
- [ ] Add MIT license and public-project policies.
- [ ] Run `rg -n "GAV|Power BI|Fabric|Cosmos|POWER_BI|OPENAI_API_KEY=.*[^$]" .` and inspect every match; only intentional exclusion/documentation mentions may remain.
- [ ] Commit with `git add .; git commit -m "docs: prepare OpenContext for open source"`.

### Task 7: Build the React/Vite portfolio UI

**Files:**
- Create: `ui/package.json`
- Create: `ui/index.html`
- Create: `ui/src/main.jsx`
- Create: `ui/src/App.jsx`
- Create: `ui/src/styles.css`
- Create: `ui/vite.config.js`

**Interfaces:**
- UI calls `POST ${VITE_API_BASE_URL}/ask` and renders `answer`, `confidence`, and `sources`.
- UI calls `POST ${VITE_API_BASE_URL}/search` for evidence-only mode.

- [ ] Implement a single-page layout with product name, query composer, example prompts, answer card, source cards, loading state, and error state.
- [ ] Run `npm install` and `npm run build` in `ui`; confirm the build fails only before files exist.
- [ ] Add the implementation and a responsive visual system suitable for a portfolio screenshot.
- [ ] Run `npm run build` and confirm exit code 0.
- [ ] Commit with `git add ui; git commit -m "feat: add OpenContext demo UI"`.

### Task 8: Final integration and hygiene verification

**Files:**
- Modify: `README.md`
- Modify: `docs/quickstart.md`
- Test: `tests/test_integration.py`

- [ ] Add an integration test that creates a temporary corpus, builds the index, searches it, and asks a grounded question through the FastAPI test client.
- [ ] Run `python -m pytest -q` and confirm all tests pass.
- [ ] Run `python -m ruff check opencontext api serve.py tests` and fix all reported errors.
- [ ] Run `npm run build` in `ui` and confirm exit code 0.
- [ ] Run `git status --short`, `git diff --check`, and credential/proprietary-content scans.
- [ ] Update the README with the final verified commands and commit with `git add .; git commit -m "chore: verify OpenContext release baseline"`.
