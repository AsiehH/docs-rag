import logging
import time

from openai import OpenAI

from app.settings import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def embed_texts(texts: list[str], client: OpenAI) -> list[list[float]]:
    """
    Embed a list of texts using the OpenAI API.

    Args:
        texts (list[str]): A list of strings to be embedded.
        client (OpenAI): An instance of the OpenAI client.

    Returns:
        list[list[float]]: A list of embeddings, where each embedding is a list of floats.
    """
    if not texts:
        return []

    start = time.perf_counter()
    response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)

    latency_seconds = time.perf_counter() - start
    logger.info(
        "Embedded %d texts: %d tokens, %.2fs",
        len(texts),
        response.usage.total_tokens,
        latency_seconds,
    )

    return [item.embedding for item in response.data]
