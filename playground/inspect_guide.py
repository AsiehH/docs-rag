"""Print the cleaned text of one cached guide and basic paragraph stats.

Run from the project root:
    uv run python -m playground.inspect_guide
"""

from app.ingest import extract_text, html_to_text, load_guide
from app.settings import CHUNK_SIZE

GUIDE_PATH = "guidance/food-products-and-vat-notice-70114"
PREVIEW_CHARS = 3000


def main() -> None:
    text = html_to_text(extract_text(load_guide(GUIDE_PATH)))
    print(text[:PREVIEW_CHARS])
    print("---")

    paragraphs = text.split("\n\n")
    paragraph_lengths = [len(paragraph) for paragraph in paragraphs]
    print("chars:", len(text))
    print("paragraphs:", len(paragraphs))
    print("longest paragraph:", max(paragraph_lengths))
    print(
        f"paragraphs over CHUNK_SIZE ({CHUNK_SIZE}):",
        sum(length > CHUNK_SIZE for length in paragraph_lengths),
    )


if __name__ == "__main__":
    main()
