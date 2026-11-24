"""Sanity-check chunk_text on toy inputs and one real cached guide.

Run from the project root:
    uv run python -m playground.check_chunking
"""

from app.ingest import chunk_text, extract_text, html_to_text, load_guide
from app.settings import CHUNK_OVERLAP, CHUNK_SIZE

GUIDE_PATH = "guidance/food-products-and-vat-notice-70114"


def main() -> None:
    oversized_paragraph = "a" * 600
    print(
        "oversized paragraph:",
        [len(c) for c in chunk_text(oversized_paragraph, 250, 50)],
    )
    print("expected:           ", [250, 250, 200])

    four_paragraphs = "\n\n".join(["a" * 100] * 4)
    print(
        "four paragraphs:    ",
        [len(c) for c in chunk_text(four_paragraphs, 250, 50)],
    )
    print("expected:           ", [202, 152, 152])
    print("---")

    text = html_to_text(extract_text(load_guide(GUIDE_PATH)))
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    chunk_lengths = [len(chunk) for chunk in chunks]
    print("real guide chunks:", len(chunks))
    print("longest chunk:", max(chunk_lengths), f"(limit {CHUNK_SIZE})")
    print("shortest chunk:", min(chunk_lengths))
    print("---")
    print(chunks[0])


if __name__ == "__main__":
    main()
