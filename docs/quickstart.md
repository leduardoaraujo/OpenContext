# Quickstart

1. Install Python 3.11+ and Node.js 18+.
2. Install Python dependencies with `python -m pip install -e ".[dev]"`.
3. Start the API with `python -m uvicorn serve:app --reload`.
4. Index `examples/knowledge` using the UI or `POST /documents/index`.
5. Ask a question in the UI or call `POST /ask`.
6. Run `python -m pytest -q` and `npm run build` before sharing changes.

No external API key is required. The optional `.env` file only changes local paths and embedding dimension in this first version.
