# Architecture

```text
Markdown corpus -> loader -> chunker -> embeddings -> SQLite index
                                                   |
                                  search / ask <- retriever <- FastAPI <- React UI
```

The `opencontext` package is the reusable core. `OpenContextService` is the boundary used by the API and can also be embedded in another Python application. The service never fabricates a numeric claim: when retrieval has no positive evidence it returns an explicit insufficient-context response.

The first release uses deterministic hash embeddings so a new contributor can run the complete demo without downloading a model or configuring an external provider. This is a portfolio-friendly baseline, not a claim that hashing is the best semantic retrieval method for production.
