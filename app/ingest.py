import json
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from app.settings import GUIDES_FILE, RAW_DIR

logger = logging.getLogger(__name__)

HEADING_TAGS = ["h2", "h3", "h4"]
BLOCK_TAGS = ["p", "li", "tr", "div"]


def load_guide_paths(guides_file: Path = GUIDES_FILE) -> list[str]:
    """Read GOV.UK guide paths from a text file, skipping blank and comment lines."""
    guide_paths = []
    for line in guides_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            guide_paths.append(line)
    logger.info("Loaded %d guide paths from %s", len(guide_paths), guides_file)
    return guide_paths


def fetch_guide(path: str) -> dict:
    """Fetch the content of a GOV.UK guide given its path."""
    url = f"https://www.gov.uk/api/content/{path}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def load_guide(path: str, raw_dir: Path = RAW_DIR) -> dict:
    """Return a guide's API content, reading from the local cache if present."""
    cache_file = raw_dir / f"{path.replace('/', '__')}.json"
    if cache_file.exists():
        logger.info("Cache hit: %s", path)
        return json.loads(cache_file.read_text())

    logger.info("Fetching: %s", path)
    content = fetch_guide(path)
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(content))
    return content


def extract_text(content: dict) -> str:
    """Return the HTML body of a GOV.UK content item, handling both page shapes."""
    details = content["details"]

    if "parts" in details:
        sections = []
        for part in details["parts"]:
            sections.append(f"<h2>{part['title']}</h2>\n{part['body']}")
        return "\n".join(sections)

    if "body" in details:
        return details["body"]

    raise ValueError(f"No text found for {content.get('base_path')}")


def html_to_text(html: str) -> str:
    """Convert GOV.UK HTML to plain text, keeping paragraph breaks and headings."""
    soup = BeautifulSoup(html, "html.parser")

    for heading in soup.find_all(HEADING_TAGS):
        level = int(heading.name[1])
        heading_text = " ".join(heading.get_text().split())
        heading.replace_with(f"\n\n{'#' * level} {heading_text}\n\n")

    for block in soup.find_all(BLOCK_TAGS):
        block.append("\n")

    text = soup.get_text()
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_fixed_size(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into chunks of at most chunk_size characters.

    A fixed window that cuts wherever the chunk_size limit is reached,
    regardless of paragraph boundaries. Each window starts chunk_overlap
    characters before the previous one ended.
    """
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap")
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break

        start += chunk_size - chunk_overlap
    return chunks


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into chunks of at most chunk_size characters, preserving paragraph boundaries.

    Each chunk after the first starts with the previous chunk's last chunk_overlap chars.
    """
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap")

    paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
            pieces = split_fixed_size(paragraph, chunk_size, chunk_overlap)
            chunks.extend(pieces[:-1])
            current_chunk = pieces[-1]
        else:
            candidate_chunk = (
                current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            )
            if len(candidate_chunk) <= chunk_size:
                current_chunk = candidate_chunk
            else:
                chunks.append(current_chunk)
                overlap_text = (
                    current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
                )
                candidate_chunk = (
                    overlap_text + "\n\n" + paragraph if overlap_text else paragraph
                )
                if len(candidate_chunk) <= chunk_size:
                    current_chunk = candidate_chunk
                else:
                    current_chunk = paragraph
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
