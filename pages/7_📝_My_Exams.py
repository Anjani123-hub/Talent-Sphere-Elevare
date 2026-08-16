from __future__ import annotations

from datetime import datetime
import streamlit as st

from src.auth_ui import (
    require_login,
    load_css,
    sidebar_user_panel,
)

from src.exam_db import get_all_exams, delete_expired_exams

st.set_page_config(
    page_title="My Exams",
    page_icon="📝",
    layout="wide",
)

require_login()
load_css()
sidebar_user_panel()

st.title("📝 My Exams")

delete_expired_exams()
exams = get_all_exams()

if not exams:
    st.info("No exams available.")
    st.stop()

now = datetime.now()

for exam in exams:

    exam_id = exam[0]
    title = exam[1]
    subject = exam[2]
    topic = exam[3]
    difficulty = exam[4]
    total_questions = exam[5]
    exam_date = exam[6]
    start_time = exam[7]
    end_time = exam[8]
    created_by = exam[9]

    exam_start = datetime.strptime(
        f"{exam_date} {start_time}",
        "%Y-%m-%d %H:%M:%S"
    )

    exam_end = datetime.strptime(
        f"{exam_date} {end_time}",
        "%Y-%m-%d %H:%M:%S"
    )

    with st.container(border=True):

        st.subheader(title)

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Subject:** {subject}")
            st.write(f"**Topic:** {topic}")
            st.write(f"**Difficulty:** {difficulty}")

        with col2:
            st.write(f"**Questions:** {total_questions}")
            st.write(f"**Date:** {exam_date}")
            st.write(f"**Time:** {start_time} - {end_time}")

        # -----------------------------
        # Exam Status
        # -----------------------------

        if now < exam_start:

            st.info(f"⏳ Exam starts on {exam_date} at {start_time}")

        elif now > exam_end:

            st.error("🔒 Exam Closed")

        else:

            st.success("🟢 Exam is Live")

            if st.button("📝 Start Exam", key=f"exam_{exam_id}"):

                st.session_state.exam_id = exam_id

                st.switch_page("pages/8_📝_Take_Exam.py")