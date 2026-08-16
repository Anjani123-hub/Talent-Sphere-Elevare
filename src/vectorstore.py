"""
src/vectorstore.py
--------------------
Talks to ChromaDB — stores document chunks as vectors so they can
be searched by meaning, and tracks which files were already
ingested (by file hash) so re-uploading the same PDF is skipped.

Every chunk is tagged in its metadata with:
    source -> the original filename
    page   -> the page number it came from
    hash   -> the fingerprint of the whole file it came from

That "hash" tag is what powers de-duplication (`ingested_hashes`)
and correct running totals (`stats`) — new files always ADD to the
collection, they never overwrite what's already indexed. Only
`reset_collection()` wipes everything.
"""

import chromadb
from src.config import CHROMA_DB_PATH, CHROMA_COLLECTION


def get_client():
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_collection():
    client = get_client()
    return client.get_or_create_collection(name=CHROMA_COLLECTION)


def add_chunks(chunks: list[dict], embeddings: list[list[float]], digest: str) -> int:
    """
    Store this file's chunks. `digest` is the file_hash of the
    whole PDF, stamped onto every chunk's metadata for later
    de-duplication. Returns how many chunks were added.
    """
    if not chunks:
        return 0

    collection = get_collection()
    ids = [f"{digest}_{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "page": c["page"], "hash": digest} for c in chunks]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    return len(chunks)


def ingested_hashes() -> set[str]:
    """Every unique file-hash already present in the index."""
    collection = get_collection()
    if collection.count() == 0:
        return set()
    data = collection.get(include=["metadatas"])
    return {m["hash"] for m in data["metadatas"] if "hash" in m}


def stats() -> dict:
    """Summary numbers shown on the Ingest page and the sidebar."""
    collection = get_collection()
    total_chunks = collection.count()
    if total_chunks == 0:
        return {"sources": 0, "total_chunks": 0, "source_names": []}

    data = collection.get(include=["metadatas"])
    source_names = sorted({m["source"] for m in data["metadatas"] if "source" in m})
    return {
        "sources": len(source_names),
        "total_chunks": total_chunks,
        "source_names": source_names,
    }


def search(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """Run a similarity search and return simple, ready-to-display dicts."""
    collection = get_collection()
    if collection.count() == 0:
        return []

    raw = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    documents = raw["documents"][0]
    metadatas = raw["metadatas"][0]
    distances = raw["distances"][0]

    results = []
    for doc, meta, distance in zip(documents, metadatas, distances):
        similarity = max(0.0, round(1 - distance, 3))
        results.append({
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", "?"),
            "score": similarity,
            "text": doc,
        })
    return results


def reset_collection():
    """Permanently delete every chunk from the index."""
    client = get_client()
    try:
        client.delete_collection(name=CHROMA_COLLECTION)
    except Exception:
        pass
    return client.get_or_create_collection(name=CHROMA_COLLECTION)

def get_all_documents():
    """
    Return all indexed document chunks from ChromaDB.
    Used for document-wide AI operations such as
    summarization and key-point extraction.
    """

    collection = get_collection()

    if collection.count() == 0:
        return []

    data = collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )

    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])

    results = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        results.append(
            {
                "text": document,
                "source": metadata.get(
                    "source",
                    "Unknown"
                ),
                "page": metadata.get(
                    "page",
                    "?"
                ),
            }
        )

    return results