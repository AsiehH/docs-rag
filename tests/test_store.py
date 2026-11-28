import logging
from pathlib import Path

import chromadb
import pytest
from chromadb import Collection

from app.store import store_chunks

SOURCE = "guidance/example-guide"
CHUNKS = ["first chunk", "second chunk", "third chunk"]
VECTORS = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


@pytest.fixture
def collection(tmp_path: Path) -> Collection:
    """A real Chroma collection in a temporary folder, deleted after each test."""
    client = chromadb.PersistentClient(path=tmp_path)
    return client.get_or_create_collection(
        name="test_collection",
        configuration={"hnsw": {"space": "cosine"}},
        embedding_function=None,
    )


def test_store_chunks_stores_every_chunk_with_id_and_metadata(collection):
    store_chunks(collection, CHUNKS, VECTORS, SOURCE)

    assert collection.count() == 3
    record = collection.get(ids=[f"{SOURCE}::1"])
    assert record["documents"] == ["second chunk"]
    assert record["metadatas"] == [{"source": SOURCE, "chunk_index": 1}]


def test_store_chunks_twice_does_not_duplicate(collection):
    store_chunks(collection, CHUNKS, VECTORS, SOURCE)
    store_chunks(collection, CHUNKS, VECTORS, SOURCE)

    assert collection.count() == 3


def test_store_chunks_mismatched_lengths_raises(collection):
    with pytest.raises(ValueError):
        store_chunks(collection, CHUNKS, VECTORS[:2], SOURCE)


def test_store_chunks_empty_input_stores_nothing_and_warns(collection, caplog):
    with caplog.at_level(logging.WARNING, logger="app.store"):
        store_chunks(collection, [], [], SOURCE)

    assert collection.count() == 0
    assert SOURCE in caplog.text
