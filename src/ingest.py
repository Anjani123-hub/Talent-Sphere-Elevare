"""
src/ingest.py
--------------
Turns an uploaded PDF into chunks ready to embed:

    extract_pages(file)          -> list of {"page": n, "text": "..."}
    chunk_pages(pages, filename) -> list of {"text","source","page"} chunks
    file_hash(data: bytes)       -> a stable fingerprint used to detect
                                     "have I already ingested this exact
                                     file before?" (de-duplication)
"""

import hashlib
from pypdf import PdfReader
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_pages(file) -> list[dict]:
    """Read a PDF and return the text of every non-empty page."""
    reader = PdfReader(file)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page": i, "text": text})
    return pages


def _split_with_overlap(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += max(chunk_size - overlap, 1)
    return chunks


def chunk_pages(pages: list[dict], filename: str) -> list[dict]:
    """
    Split every page's text into overlapping chunks.
    Each returned chunk is a dict: {"text", "source", "page"}.
    """
    chunks = []
    for page_info in pages:
        page_num = page_info["page"]
        page_text = page_info["text"]
        for piece in _split_with_overlap(page_text, CHUNK_SIZE, CHUNK_OVERLAP):
            chunks.append({
                "text": piece,
                "source": filename,
                "page": page_num,
            })
    return chunks


def file_hash(data: bytes) -> str:
    """A stable fingerprint of the raw file bytes, used for de-duplication."""
    return hashlib.sha256(data).hexdigest()