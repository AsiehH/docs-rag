"""Sanity-check store_chunks on one real cached guide (makes ONE real embedding API call).

Writes to the real Chroma folder (CHROMA_DIR). Safe to re-run: ids are
deterministic and store_chunks upserts, so the count should stay the same.

Run from the project root:
    uv run python -m playground.check_store
"""

import logging

import chromadb
from openai import OpenAI

from app.embed import embed_texts
from app.ingest import chunk_text, extract_text, html_to_text, load_guide
from app.settings import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    OPENAI_API_KEY,
)
from app.store import store_chunks

GUIDE_PATH = "guidance/food-products-and-vat-notice-70114"


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={"hnsw": {"space": "cosine"}},
        embedding_function=None,
    )

    text = html_to_text(extract_text(load_guide(GUIDE_PATH)))
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    vectors = embed_texts(chunks, client=openai_client)
    store_chunks(collection, chunks, vectors, GUIDE_PATH)

    print("collection count:", collection.count())
    record = collection.get(ids=[f"{GUIDE_PATH}::0"], include=["documents", "metadatas"])
    print("first record metadata:", record["metadatas"][0])
    print("first record text:", record["documents"][0][:200])


if __name__ == "__main__":
    main()
