from __future__ import annotations

import streamlit as st

from src.auth_ui import require_login, load_css, sidebar_user_panel
from src.exam_db import get_questions, save_result

st.set_page_config(
    page_title="Take Exam",
    page_icon="📝",
    layout="wide",
)

require_login()
load_css()
sidebar_user_panel()

if "exam_id" not in st.session_state:
    st.error("No exam selected.")
    st.stop()

exam_id = st.session_state.exam_id

questions = get_questions(exam_id)

if not questions:
    st.warning("No questions available.")
    st.stop()

st.title("📝 Take Exam")

answers = {}

for q in questions:

    qid = q[0]
    question = q[1]

    st.subheader(question)

    answers[qid] = st.radio(
        "Choose one",
        [
            "-- Select an Answer --",
            q[2],
            q[3],
            q[4],
            q[5],
        ],
        key=f"q{qid}",
    )

    st.divider()

if st.button("Submit Exam"):

    # Check whether all questions are answered
    for q in questions:

        qid = q[0]

        if answers[qid] is None:
            st.error("⚠️ Please answer all questions before submitting.")
            st.stop()

    for q in questions:

        qid = q[0]

        if answers[qid] == "-- Select an Answer --":
            st.error("⚠ Please answer all questions before submitting.")
            st.stop()
    # Calculate score
    score = 0

    for q in questions:

        qid = q[0]

        correct = q[6]

        selected = answers[qid]

        option_map = {
            "A": q[2],
            "B": q[3],
            "C": q[4],
            "D": q[5],
        }

        if option_map[correct] == selected:
            score += 1

    save_result(
        exam_id,
        st.session_state.user["username"],
        score,
        len(questions),
    )

    st.success(f"Your Score: {score}/{len(questions)}")

    st.switch_page("pages/9_📊_Results.py")