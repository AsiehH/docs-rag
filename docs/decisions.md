# Design Decisions

Choices made while building, with the options considered and why one won.
These feed the README's "Trade-offs" section in Step 5.

## Embedding model (Step 1)

- **Status:** chosen: A (2026-11-25)
- **Context:** the pipeline is `load → extract → html_to_text → chunk`. Next, each chunk
  is turned into a vector and then stored in Chroma.

| Option | Pros | Cons |
|---|---|---|
| **A. OpenAI `text-embedding-3-small`, called explicitly** | `openai` SDK and API key already in use. Good quality. Very cheap (a few cents for the whole corpus). Same call pattern as `generate.py`. | Paid API call; needs network. |
| **B. Chroma's built-in default** (`all-MiniLM-L6-v2`, local) | Free, offline. Chroma embeds automatically. | Embedding is hidden inside Chroma, so it's harder to explain and log. Tied to Chroma, so it must be redone for pgvector in Step 5. Lower quality. |
| **C. `sentence-transformers`** (local model) | Free, any model. | Heavy dependency (PyTorch, ~1 GB). Too much for this project. |

- **Recommendation:** A. Our code calls the embedding API and passes the vectors to Chroma,
  so we control the step: log token usage and latency, mock it in tests, and keep it
  unchanged when moving to pgvector. The vector store only stores and searches.

### Plan if A is chosen

1. Add `EMBEDDING_MODEL = "text-embedding-3-small"` to `app/settings.py`.
2. Write `embed_texts(texts: list[str]) -> list[list[float]]`: one batched API call,
   logging token usage and latency.
3. Unit test with a mocked OpenAI client (no real API call in tests).
4. Run once on the food guide's 111 chunks to check the vector shape (1536 dimensions).
5. Add `chromadb` as a dependency, then store chunks with their metadata.
