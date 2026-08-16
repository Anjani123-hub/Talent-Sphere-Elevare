"""
src/workspace_pages.py
------------------------
Pages both Admins and regular Users can see:
  - documents_page(): a read-only list of what's indexed
    (uploading happens on the admin-only Document Ingestion page)
  - coming_soon(): a shared placeholder for AI Assistant / Exams /
    Announcements, until those phases are built
"""

import streamlit as st

from src.auth_ui import require_login, load_css, sidebar_user_panel
from src.vectorstore import stats


def documents_page():
    require_login()
    load_css()
    sidebar_user_panel()

    st.markdown(
        """<div class="hero-section">
<h1>📄 Documents</h1>
<p>Everything currently indexed in the knowledge base.</p>
</div>""",
        unsafe_allow_html=True,
    )

    st.write("")

    index = stats()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Documents", index["sources"])
    with c2:
        st.metric("Total Chunks", index["total_chunks"])

    st.write("")

    if index["source_names"]:
        for name in index["source_names"]:
            st.markdown(f'<div class="document-card">📄 {name}</div>', unsafe_allow_html=True)
    else:
        st.info("No documents indexed yet.")

    user = st.session_state.get("user")
    if user and user.get("role") == "admin":
        st.write("")
        st.caption("To upload or remove documents, use **Document Ingestion** in the Administration menu.")


def coming_soon(title: str, description: str, icon: str = "🚧"):
    require_login()
    load_css()
    sidebar_user_panel()

    st.markdown(
        f"""<div class="hero-section">
<h1>{icon} {title}</h1>
<p>{description}</p>
</div>""",
        unsafe_allow_html=True,
    )

    st.write("")
    st.info(f"{title} isn't built yet — it's next on the roadmap. Checking back soon!")