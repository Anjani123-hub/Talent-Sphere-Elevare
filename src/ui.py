"""
src/ui.py
Reusable UI components for TalentSphere AI

IMPORTANT: every HTML string below is written flush-left with NO
blank lines in the middle of the tags. Streamlit's markdown
renderer can lose track of "this is HTML" if a blank line appears
partway through a block — everything after that blank line then
prints as literal text instead of rendering. Keep that in mind if
you edit these.
"""

import streamlit as st
from src.auth_ui import load_css


def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""<div class="hero-section">
<h1>{title}</h1>
<p>{subtitle}</p>
</div>""",
        unsafe_allow_html=True,
    )


def card(title: str, body: str, icon: str = "📄"):
    st.markdown(
        f"""<div class="info-card">
<div class="card-icon">{icon}</div>
<h3>{title}</h3>
<p>{body}</p>
</div>""",
        unsafe_allow_html=True,
    )


def metric_tile(label: str, value):
    st.markdown(
        f"""<div class="metric-card">
<div class="metric-value">{value}</div>
<div class="metric-label">{label}</div>
</div>""",
        unsafe_allow_html=True,
    )


def empty_state(
    title="Nothing Here Yet",
    subtitle="Upload documents to begin.",
    icon="📂",
):
    st.markdown(
        f"""<div class="empty-card">
<div class="empty-icon">{icon}</div>
<h2>{title}</h2>
<p>{subtitle}</p>
</div>""",
        unsafe_allow_html=True,
    )


def result_card(source, page, score, text):
    st.markdown(
        f"""<div class="result-card">
<div class="result-top">
<div>
<strong>📄 {source}</strong><br>
<span>Page {page}</span>
</div>
<div class="score-badge">{round(score, 3)}</div>
</div>
<div class="result-text">{text}</div>
</div>""",
        unsafe_allow_html=True,
    )


def dashboard_banner(user):
    st.markdown(
        f"""<div class="dashboard-banner">
<h1>👋 Welcome, {user}</h1>
<p>TalentSphere AI is ready. Upload documents and perform intelligent semantic search.</p>
</div>""",
        unsafe_allow_html=True,
    )


def quick_action(title, description, emoji):
    st.markdown(
        f"""<div class="quick-card">
<div style="font-size:45px;">{emoji}</div>
<h3>{title}</h3>
<p>{description}</p>
</div>""",
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        """<hr>
<center><small>
TalentSphere AI © 2026<br>
Built using Streamlit • ChromaDB • SentenceTransformers
</small></center>""",
        unsafe_allow_html=True,
    )