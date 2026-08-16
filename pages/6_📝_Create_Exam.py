from __future__ import annotations

import streamlit as st

from src.auth_ui import require_login, load_css, sidebar_user_panel
from src.exam_db import create_exam, get_questions
from src.exam_db import create_exam, delete_expired_exams
from src.exam_generator import generate_exam

st.set_page_config(
    page_title="Create Exam",
    page_icon="📝",
    layout="wide",
)

require_login()
load_css()
sidebar_user_panel()
delete_expired_exams()

user = st.session_state.user

if user["role"] != "admin":
    st.error("Only administrators can access this page.")
    st.stop()

st.title("📝 Create AI Exam")

with st.form("exam_form"):

    title = st.text_input("Exam Title")

    subject = st.text_input("Subject")

    topic = st.text_input("Topic")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
    )

    total_questions = st.number_input(
        "Number of Questions",
        min_value=5,
        max_value=50,
        value=10,
    )

    exam_date = st.date_input("📅 Exam Date")

    start_time = st.time_input("🕒 Start Time")

    end_time = st.time_input("🕔 End Time")

    submit = st.form_submit_button("Create Exam")


if submit:

    try:

        exam_id = create_exam(
            title,
            subject,
            topic,
            difficulty,
            total_questions,
            str(exam_date),
            str(start_time),
            str(end_time),
            user["username"],
        )

        with st.spinner(
            "🤖 AI is generating exam questions..."
        ):

            questions = generate_exam(
                exam_id,
                subject,
                topic,
                difficulty,
                total_questions,
            )

        st.success(
            f"✅ Exam Created Successfully! "
            f"{len(questions)} questions generated."
        )

        st.info(
            "Students can now find this exam "
            "in the My Exams section."
        )

    except Exception as e:

        st.error(
            f"❌ Failed to create exam: {e}"
        )