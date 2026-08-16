"""
src/embeddings.py
-------------------
Turns text into vectors using the embedding model named in your
.env (BAAI/bge-large-en-v1.5 by default). The model loads once and
is cached, since loading it is slow.
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL


@st.cache_resource(show_spinner="Loading embedding model...")
def get_model():
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed a list of document chunks (used during ingestion)."""
    model = get_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a single search query."""
    return embed_documents([text])[0]