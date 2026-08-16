# Talent Sphere Elevate — Milestone 1

**AI training & knowledge assistant — retrieval foundation.**

Milestone 1 is a themed, multipage Streamlit app that ingests training PDFs,
chunks and embeds them with `BAAI/bge-large-en-v1.5`, stores the vectors in a
persistent ChromaDB index, and lets you run **semantic search** that returns the
most relevant passages **with their sources and similarity scores**.

> This milestone deliberately contains **no LLM / answer generation**. It proves
> that retrieval finds the right passages *before* an LLM is layered on in
> Milestone 2.

---

## Prerequisites

- **Python 3.10+**
- ~1.3 GB free disk for the embedding model (downloaded on first run)
- CPU is sufficient; a CUDA GPU is used automatically if available.

## Setup & Run

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app (first run downloads the ~1.3GB embedding model)
streamlit run app.py
```

Then, in the browser:

1. Open the **📥 Ingest** page → upload one or more PDFs → click **Build Index**.
2. Open the **🔍 Search** page → type a question → click **Search**.
3. Review the ranked passages, each showing **source filename, page, and score**.

The index is persisted to `./chroma_db`, so your data survives an app restart.
Re-uploading the same PDF is de-duplicated by file hash — no duplicate chunks.

> **First run:** the model download (~1.3 GB) happens once and is cached by
> `sentence-transformers`. A spinner communicates progress. Encoding on CPU is
> slower than tiny models — a progress bar is shown during ingestion.

---

## Configuration

All settings live in `.env` (copy from `.env.example`). Defaults:

| Setting              | Default                     |
|----------------------|-----------------------------|
| `EMBEDDING_MODEL`    | `BAAI/bge-large-en-v1.5`    |
| `CHROMA_DB_PATH`     | `./chroma_db`               |
| `CHROMA_COLLECTION`  | `talent_sphere_docs`        |
| `CHUNK_SIZE`         | `800`                       |
| `CHUNK_OVERLAP`      | `150`                       |
| `TOP_K`              | `5`                         |
| `DOCUMENTS_DIR`      | `./documents`               |

Embedding dimension is **1024**; the Chroma collection uses **cosine** distance.

---

## Folder Structure

```
Talent_Sphere/
├── .streamlit/
│   └── config.toml          # Streamlit base theme (LinkedIn colors)
├── app.py                   # Home page + entry point
├── pages/
│   ├── 1_📥_Ingest.py       # Upload + build index
│   └── 2_🔍_Search.py       # Semantic search
├── src/
│   ├── __init__.py
│   ├── config.py            # Settings loaded from .env
│   ├── ingest.py            # PDF extraction + chunking + hashing
│   ├── embeddings.py        # Load BGE model, encode docs/queries
│   ├── vectorstore.py       # Chroma client, add, query, dedup, stats
│   └── ui.py                # load_css(), hero(), card(), badges…
├── documents/               # place source PDFs here (gitignored)
├── assets/
│   └── styles.css           # Enterprise LinkedIn-theme CSS
├── chroma_db/               # persistent index (gitignored, auto-created)
├── .env / .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

**Separation rule:** `src/` holds reusable, importable logic (no Streamlit calls
except in `ui.py`). `app.py` and `pages/` stay thin and call into `src/`, so
Milestones 2–4 (LLM answers, grading, analytics) can layer on cleanly.

---

## How retrieval works (BGE specifics)

- Documents and queries are encoded with `normalize_embeddings=True` (cosine space).
- **Queries only** are prefixed with the BGE instruction:
  `"Represent this sentence for searching relevant passages: "`.
- Results are scored as `score = 1 - cosine_distance` (higher = more similar).