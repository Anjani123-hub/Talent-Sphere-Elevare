from __future__ import annotations

import sqlite3
import pandas as pd
import streamlit as st

from src.auth_ui import require_login, load_css, sidebar_user_panel

st.set_page_config(
    page_title="Results",
    page_icon="📊",
    layout="wide",
)

require_login()
load_css()
sidebar_user_panel()

st.title("📊 Exam Results")

user = st.session_state.user

conn = sqlite3.connect("talentsphere.db")

# -------------------------------
# ADMIN
# -------------------------------
if user["role"] == "admin":

    query = """
    SELECT
        username AS Student,
        exam_id AS Exam_ID,
        score AS Score,
        total AS Total,
        ROUND(score*100.0/total,2) AS Percentage,
        submitted_at AS Submitted_Time
    FROM results
    ORDER BY submitted_at DESC
    """

    df = pd.read_sql_query(query, conn)

# -------------------------------
# USER
# -------------------------------
else:

    query = """
    SELECT
        exam_id AS Exam_ID,
        score AS Score,
        total AS Total,
        ROUND(score*100.0/total,2) AS Percentage,
        submitted_at AS Submitted_Time
    FROM results
    WHERE username = ?
    ORDER BY submitted_at DESC
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(user["username"],)
    )

conn.close()

if df.empty:

    st.info("No results available.")

else:

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # Only admin can download all results
    if user["role"] == "admin":

        st.download_button(
            "📥 Download Results",
            df.to_csv(index=False),
            "results.csv",
            "text/csv",
        )