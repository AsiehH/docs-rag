import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
MODEL_NAME: str = "gpt-4o-mini"
TOP_K: int = 5
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 50

GUIDES_FILE: Path = Path("data/guides.txt")
RAW_DIR: Path = Path("data/raw")
