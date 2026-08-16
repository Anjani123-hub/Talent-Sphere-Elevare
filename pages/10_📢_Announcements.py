from __future__ import annotations

import streamlit as st

from src.auth_ui import require_login, load_css, sidebar_user_panel
from src.exam_db import add_announcement, get_announcements

st.set_page_config(
    page_title="Announcements",
    page_icon="📢",
    layout="wide",
)

require_login()
load_css()
sidebar_user_panel()

user = st.session_state.user

st.title("📢 Announcements")

if user["role"] == "admin":

    with st.form("announcement"):

        title = st.text_input("Title")

        message = st.text_area("Message")

        submit = st.form_submit_button("Post")

    if submit:

        add_announcement(
            title,
            message,
            user["username"],
        )

        st.success("Announcement Posted")

st.divider()

rows = get_announcements()

if not rows:

    st.info("No announcements available.")

else:

    for row in rows:

        with st.container(border=True):

            st.subheader(row[1])

            st.write(row[2])

            st.caption(
                f"Posted by {row[3]} | {row[4]}"
            )