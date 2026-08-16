from __future__ import annotations

import time
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from src.auth_ui import (
    load_css,
    require_login,
    sidebar_user_panel,
)

from src.config import TOP_K
from src.embeddings import embed_query
from src.vectorstore import (
    search,
    get_all_documents,
)

from src.llm import (
    ask_llm,
    summarize_document,
    extract_key_points,
    compare_documents,
)

from src.ui import section_header


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Search",
    page_icon="🤖",
    layout="wide",
)


# =========================================================
# AUTHENTICATION
# =========================================================

require_login()
load_css()
sidebar_user_panel()


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.divider()

    st.subheader("🤖 AI Tools")

    tool = st.selectbox(
        "Choose AI Tool",
        [
            "Ask Question",
            "Summarize Documents",
            "Extract Key Points",
            "Compare Topics",
        ],
    )

    st.divider()

    if st.button(
        "🗑 Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# HEADER
# =========================================================

section_header(
    "🤖 TalentSphere AI",
    "Analyze your uploaded documents using AI.",
)


# =========================================================
# WELCOME MESSAGE
# =========================================================

if len(st.session_state.messages) == 0:

    with st.chat_message("assistant"):

        st.markdown(
            """
👋 **Welcome to TalentSphere AI!**

I can help you analyze your uploaded documents.

### Available AI Tools

💬 **Ask Question**  
Ask questions about your uploaded PDFs.

📄 **Summarize Documents**  
Generate a structured summary.

🔑 **Extract Key Points**  
Find the most important information.

📊 **Compare Topics**  
Generate comparison tables from your documents.
"""
        )


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# USER INPUT
# =========================================================

if tool == "Ask Question":

    question = st.chat_input(
        "Ask TalentSphere AI anything..."
    )

elif tool == "Summarize Documents":

    all_documents = get_all_documents()

    context = ""

    relevant_results = []

    for item in all_documents:

        relevant_results.append(item)

        context += f"""

Source: {item['source']}

Page: {item['page']}

{item['text']}

------------------------------
"""

    if not context.strip():

        answer = (
            "⚠️ No uploaded documents "
            "are available to summarize."
        )

    else:

        answer = summarize_document(
            context
        )

elif tool == "Extract Key Points":

    all_documents = get_all_documents()

    context = ""

    relevant_results = []

    for item in all_documents:

        relevant_results.append(item)

        context += f"""

Source: {item['source']}

Page: {item['page']}

{item['text']}

------------------------------
"""

    if not context.strip():

        answer = (
            "⚠️ No uploaded documents "
            "are available."
        )

    else:

        answer = extract_key_points(
            context
        )

else:

    question = st.chat_input(
        "What two topics or concepts do you want to compare?"
    )


# =========================================================
# PROCESS REQUEST
# =========================================================

if question:

    start = time.time()

    # -----------------------------------------------------
    # SHOW USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # -----------------------------------------------------
    # AI RESPONSE
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 TalentSphere AI is analyzing..."
        ):

            # =================================================
            # ASK QUESTION
            # =================================================

            if tool == "Ask Question":

                vector = embed_query(
                    question
                )

                results = search(
                    vector,
                    TOP_K
                )

                context = ""

                relevant_results = []

                for item in results:

                    if item["score"] >= 0.40:

                        relevant_results.append(
                            item
                        )

                        context += f"""

Source: {item['source']}

Page: {item['page']}

{item['text']}

------------------------------
"""

                # If no relevant document is found,
                # ask_llm will use general knowledge.

                if not context.strip():

                    context = """
No relevant information was found in the
uploaded documents.
"""

                answer = ask_llm(
                    question=question,
                    context=context,
                    history=st.session_state.messages,
                )


            # =================================================
            # SUMMARIZE DOCUMENTS
            # =================================================

            elif tool == "Summarize Documents":

                # Get a broad query to retrieve document content
                vector = embed_query(
                    "important topics main concepts summary"
                )

                results = search(
                    vector,
                    TOP_K
                )

                context = ""

                relevant_results = []

                for item in results:

                    relevant_results.append(
                        item
                    )

                    context += f"""

Source: {item['source']}

Page: {item['page']}

{item['text']}

------------------------------
"""

                if not context.strip():

                    answer = (
                        "⚠️ No uploaded document content "
                        "is available to summarize."
                    )

                else:

                    answer = summarize_document(
                        context
                    )


            # =================================================
            # EXTRACT KEY POINTS
            # =================================================

            elif tool == "Extract Key Points":

                vector = embed_query(
                    "important key points concepts definitions facts"
                )

                results = search(
                    vector,
                    TOP_K
                )

                context = ""

                relevant_results = []

                for item in results:

                    relevant_results.append(
                        item
                    )

                    context += f"""

Source: {item['source']}

Page: {item['page']}

{item['text']}

------------------------------
"""

                if not context.strip():

                    answer = (
                        "⚠️ No uploaded document content "
                        "is available."
                    )

                else:

                    answer = extract_key_points(
                        context
                    )


            # =================================================
            # COMPARE TOPICS
            # =================================================

            elif tool == "Compare Topics":

                vector = embed_query(
                    question
                )

                results = search(
                    vector,
                    TOP_K
                )

                context = ""

                relevant_results = []

                for item in results:

                    if item["score"] >= 0.30:

                        relevant_results.append(
                            item
                        )

                        context += f"""

Source: {item['source']}

Page: {item['page']}

{item['text']}

------------------------------
"""

                if not context.strip():

                    context = """
No relevant information was found in
the uploaded documents.

Use general knowledge to create the comparison.
"""

                answer = compare_documents(
                    context
                )


            # =================================================
            # INVALID TOOL
            # =================================================

            else:

                answer = (
                    "⚠️ Please select a valid AI tool."
                )

                relevant_results = []


        # =====================================================
        # DISPLAY AI ANSWER
        # =====================================================

        st.markdown(
            answer
        )


        # =====================================================
        # RESPONSE TIME
        # =====================================================

        elapsed = time.time() - start

        st.caption(
            f"⏱ Response generated in "
            f"**{elapsed:.2f} seconds**"
        )


        # =====================================================
        # DOCUMENT SOURCES
        # =====================================================

        if relevant_results:

            st.success(
                f"📚 Used "
                f"{len(relevant_results)} "
                f"document chunk(s)."
            )

            with st.expander(
                "📚 Sources from Uploaded Documents"
            ):

                shown = set()

                for item in relevant_results:

                    source = (
                        f"{item['source']} "
                        f"(Page {item['page']})"
                    )

                    if source not in shown:

                        st.markdown(
                            f"""
**📄 {item['source']}**

- **Page:** {item['page']}
- **Similarity:** {item['score'] * 100:.1f}%

---
"""
                        )

                        shown.add(
                            source
                        )


        # =====================================================
        # AI WARNING
        # =====================================================

        st.caption(
            "⚠️ AI-generated response. "
            "Please verify important information."
        )


    # =========================================================
    # SAVE ASSISTANT RESPONSE
    # =========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )