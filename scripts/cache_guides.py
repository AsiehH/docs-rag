"""Download every guide in data/guides.txt into the local cache (data/raw/).

Run from the project root:
    uv run python -m scripts.cache_guides
"""

import logging

from app.ingest import load_guide, load_guide_paths


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    for path in load_guide_paths():
        load_guide(path)


if __name__ == "__main__":
    main()
