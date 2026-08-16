"""
TalentSphere AI
Search Knowledge Base
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.auth_ui import load_css, require_login, sidebar_user_panel
from src.config import TOP_K
from src.embeddings import embed_query
from src.ui import empty_state, result_card, section_header
from src.vectorstore import search, stats

st.set_page_config(page_title="Search Knowledge Base", page_icon="🔍", layout="wide")

require_login()
load_css()
sidebar_user_panel()

section_header(
    "🔍 Search Knowledge Base",
    "Ask a question in plain language — semantic search finds the most relevant passages.",
)

st.write("")

index = stats()

if index["total_chunks"] == 0:
    empty_state(
        "No Knowledge Base Found",
        "Upload PDF documents before searching.",
        icon="📂",
    )
else:
    st.markdown("## 🔎 Ask Your Question")

    query = st.text_input(
        "",
        placeholder="Example: Explain the leave policy...",
    )

    top_k = st.slider("Results", 1, 15, TOP_K)

    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_btn = st.button(
            "🚀 Search Documents",
            use_container_width=True,
            type="primary",
            disabled=not query.strip(),
        )

    if search_btn:
        try:
            with st.spinner("Searching your knowledge base..."):
                vector = embed_query(query.strip())
                results = search(vector, top_k)
        except Exception as e:
            st.error(f"❌ Search failed: {e}")
            results = []

        st.write("")
        st.markdown("## 📑 Search Results")

        if not results:
            st.warning("No relevant information found.")
        else:
            st.success(f"Found {len(results)} relevant passages.")
            for hit in results:
                result_card(hit["source"], hit["page"], hit["score"], hit["text"])