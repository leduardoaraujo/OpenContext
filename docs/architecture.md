# Architecture

## Relationship to GAV Insights

OpenContext is the open source engine layer behind GAV Insights. The boundary is deliberate:

```text
OpenContext engine                  GAV Insights application
Markdown -> chunks -> evidence  ->  business context -> connectors -> executive answer
```

This repository demonstrates the general-purpose retrieval foundation. The private application can provide domain-specific sources, policies, orchestration, and presentation without changing the core contracts used here.

```text
Markdown corpus -> loader -> chunker -> embeddings -> SQLite index
                                                   |
                                  search / ask <- retriever <- FastAPI <- React UI
```

The `opencontext` package is the reusable core. `OpenContextService` is the boundary used by the API and can also be embedded in another Python application. The service never fabricates a numeric claim: when retrieval has no positive evidence it returns an explicit insufficient-context response.

The first release uses deterministic hash embeddings so a new contributor can run the complete demo without downloading a model or configuring an external provider. This is a portfolio-friendly baseline, not a claim that hashing is the best semantic retrieval method for production.
