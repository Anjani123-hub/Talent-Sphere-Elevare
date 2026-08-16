import streamlit as st

from src.auth_ui import (
    require_admin,
    load_css,
    sidebar_user_panel,
)

from src.auth import (
    get_all_users,
    delete_user,
)

st.set_page_config(
    page_title="Manage Users",
    page_icon="👥",
    layout="wide",
)

require_admin()
load_css()
sidebar_user_panel()

st.title("👥 Manage Users")

users = get_all_users()

st.write(f"### Total Users : {len(users)}")

st.divider()

for user in users:

    col1, col2, col3, col4 = st.columns([3,3,2,1])

    with col1:
        st.write(user["full_name"])

    with col2:
        st.write(user["email"])

    with col3:
        st.write(user["role"])

    with col4:

        if user["role"] != "admin":

            if st.button(
                "Delete",
                key=f"delete_{user['id']}"
            ):
                delete_user(user["id"])
                st.success("User deleted successfully.")
                st.rerun()