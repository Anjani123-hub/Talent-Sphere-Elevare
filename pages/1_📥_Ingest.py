"""
TalentSphere AI
Upload & Build Knowledge Base
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

from src.auth_ui import (
    require_login,
    require_admin,
    load_css,
    sidebar_user_panel,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))



from src.embeddings import embed_documents
from src.ingest import (
    chunk_pages,
    extract_pages,
    file_hash,
)

from src.vectorstore import (
    add_chunks,
    ingested_hashes,
    reset_collection,
    stats,
)

from src.ui import (
    section_header,
    metric_tile,
)

# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------



require_login()
require_admin()
load_css()
sidebar_user_panel()

# -----------------------------------------------------
# Header
# -----------------------------------------------------

section_header(
    "📤 Upload Knowledge Base",
    "Upload PDF documents to build your AI-powered knowledge base using ChromaDB and semantic embeddings."
)

st.write("")

# -----------------------------------------------------
# Upload Section
# -----------------------------------------------------

st.markdown("## 📂 Upload PDF Documents")

st.info(
    "Supported format: PDF • Multiple files supported • Duplicate files are skipped automatically."
)

uploaded = st.file_uploader(
    "",
    type=["pdf"],
    accept_multiple_files=True,
)

st.write("")

col1, col2, col3 = st.columns([1,2,1])

with col2:

    build = st.button(
        "🚀 Build Knowledge Base",
        use_container_width=True,
        disabled=not uploaded,
        type="primary",
    )

# -----------------------------------------------------
# Build Index
# -----------------------------------------------------

if build and uploaded:

    known_hashes = ingested_hashes()

    files_processed = 0
    chunks_added = 0
    duplicates = 0

    progress = st.progress(
        0.0,
        text="Initializing..."
    )

    total = len(uploaded)

    for i, file in enumerate(uploaded, start=1):

        label = f"Processing {file.name} ({i}/{total})"

        progress.progress(
            (i - 1) / total,
            text=label,
        )

        try:

            data = file.getvalue()

            digest = file_hash(data)

            if digest in known_hashes:

                duplicates += 1

                st.warning(
                    f"⚠ {file.name} already exists. Skipping duplicate."
                )

                progress.progress(
                    i / total,
                    text=label,
                )

                continue

            pages = extract_pages(file)

            if not pages:

                st.error(
                    f"No readable text found in {file.name}"
                )

                progress.progress(
                    i / total,
                    text=label,
                )

                continue

            chunks = chunk_pages(
                pages,
                file.name,
            )

            embeddings = embed_documents(
                [c["text"] for c in chunks]
            )

            added = add_chunks(
                chunks,
                embeddings,
                digest,
            )

            files_processed += 1
            chunks_added += added

            known_hashes.add(digest)

            st.success(
                f"✅ {file.name} indexed successfully ({added} chunks)"
            )

        except Exception as e:

            st.error(
                f"❌ {file.name} : {e}"
            )

        progress.progress(
            i / total,
            text=label,
        )

    progress.progress(
        1.0,
        text="Completed"
    )

    st.write("")

    st.markdown("## 📊 Build Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_tile(
            "Files Uploaded",
            files_processed,
        )

    with c2:
        metric_tile(
            "Chunks Created",
            chunks_added,
        )

    with c3:
        metric_tile(
            "Duplicates",
            duplicates,
        )
# -----------------------------------------------------
# Current Knowledge Base
# -----------------------------------------------------

st.write("")
st.markdown("---")
st.write("")

st.markdown("## 📚 Knowledge Base Statistics")

index = stats()

col1, col2 = st.columns(2)

with col1:
    metric_tile(
        "📄 Documents",
        index["sources"],
    )

with col2:
    metric_tile(
        "🧩 Chunks",
        index["total_chunks"],
    )

st.write("")

# -----------------------------------------------------
# Uploaded Documents
# -----------------------------------------------------

if index["source_names"]:

    st.markdown("### 📂 Uploaded Documents")

    for doc in index["source_names"]:

        st.markdown(
            f"""
<div style="
background:white;
padding:18px;
border-radius:14px;
margin-bottom:12px;
border-left:6px solid #2563eb;
box-shadow:0 4px 15px rgba(0,0,0,.08);
">

<h4 style="margin:0;color:#1e293b;">
📄 {doc}
</h4>

</div>
""",
            unsafe_allow_html=True,
        )

else:

    st.info(
        "No documents uploaded yet."
    )

# -----------------------------------------------------
# Reset Knowledge Base
# -----------------------------------------------------

st.write("")
st.markdown("---")
st.write("")

st.markdown("## 🗑 Reset Knowledge Base")

st.warning(
    "Deleting the knowledge base will permanently remove all indexed documents."
)

if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

if not st.session_state.confirm_reset:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        if st.button(
            "🗑 Reset Knowledge Base",
            use_container_width=True,
            type="secondary",
        ):

            st.session_state.confirm_reset = True
            st.rerun()

else:

    st.error(
        "⚠ Are you sure you want to delete all indexed documents?"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "✅ Yes, Delete Everything",
            use_container_width=True,
        ):

            reset_collection()

            st.session_state.confirm_reset = False

            st.success(
                "Knowledge Base Reset Successfully."
            )

            st.rerun()

    with c2:

        if st.button(
            "❌ Cancel",
            use_container_width=True,
        ):

            st.session_state.confirm_reset = False
            st.rerun()