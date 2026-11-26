"""Sanity-check embed_texts on one real cached guide (makes ONE real API call).

Run from the project root:
    uv run python -m playground.check_embedding
"""

import logging

from openai import OpenAI

from app.embed import embed_texts
from app.ingest import chunk_text, extract_text, html_to_text, load_guide
from app.settings import CHUNK_OVERLAP, CHUNK_SIZE, OPENAI_API_KEY

GUIDE_PATH = "guidance/food-products-and-vat-notice-70114"


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    client = OpenAI(api_key=OPENAI_API_KEY)

    text = html_to_text(extract_text(load_guide(GUIDE_PATH)))
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    vectors = embed_texts(chunks, client=client)

    print("chunks:", len(chunks))
    print("vectors:", len(vectors))
    print("dimensions:", {len(vector) for vector in vectors})
    print("first vector, first 5 values:", vectors[0][:5])


if __name__ == "__main__":
    main()
