import logging

from chromadb import Collection

logger = logging.getLogger(__name__)


def store_chunks(
    collection: Collection, chunks: list[str], vectors: list[list[float]], source: str
) -> None:
    """
    Store chunks and their corresponding vectors in a Chroma collection.

    Args:
        collection: The Chroma collection to store the data in.
        chunks (list[str]): A list of text chunks.
        vectors (list[list[float]]): A list of vectors corresponding to the chunks.
        source (str): The source identifier for the chunks.
    """
    if len(chunks) != len(vectors):
        raise ValueError("The number of chunks must match the number of vectors.")
    if not chunks:
        logger.warning("No chunks to store for source: %s", source)
        return

    collection.upsert(
        ids=[f"{source}::{chunk_index}" for chunk_index in range(len(chunks))],
        embeddings=vectors,
        documents=chunks,
        metadatas=[
            {"source": source, "chunk_index": chunk_index}
            for chunk_index in range(len(chunks))
        ],
    )
    logger.info("Stored %d chunks from %s", len(chunks), source)
