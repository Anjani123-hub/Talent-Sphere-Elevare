"""
src/admin_pages.py
--------------------
Pages only admins can see: the analytics Dashboard and User
Management. Both are guarded with require_admin() as a second
layer of defense (the sidebar navigation already hides these from
non-admins, but this stops direct access too).
"""

import streamlit as st

from src.auth_ui import require_admin, load_css, sidebar_user_panel
from src.auth import get_all_users, get_user_count, delete_user, update_user_role
from src.vectorstore import stats
from src.ui import metric_tile


def admin_dashboard_page():
    require_admin()
    load_css()
    sidebar_user_panel()

    st.markdown(
        """<div class="hero-section">
<h1>📊 Admin Dashboard</h1>
<p>Live overview of accounts and your knowledge base.</p>
</div>""",
        unsafe_allow_html=True,
    )

    st.write("")

    index = stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_tile("👥 Total Users", get_user_count())
    with c2:
        metric_tile("📄 Documents", index["sources"])
    with c3:
        metric_tile("🧩 Chunks", index["total_chunks"])
    with c4:
        metric_tile("💬 Chat Sessions", "—")

    st.caption(
        "Chat session and exam analytics will appear here once the AI Assistant "
        "and Exams features are built (Phases 3–4) — showing real zeros instead "
        "of made-up numbers until then."
    )

    st.write("")
    st.markdown("## 👥 Recently Added Users")

    users = get_all_users()
    if users:
        recent = users[:5]
        for u in recent:
            role_badge = "🛡️ Admin" if u["role"] == "admin" else "👤 User"
            st.markdown(
                f"""<div class="document-card">
{u['full_name']} · {u['email']} · {role_badge}
</div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No users yet.")


def user_management_page():
    require_admin()
    load_css()
    sidebar_user_panel()

    st.markdown(
        """<div class="hero-section">
<h1>👥 User Management</h1>
<p>View every account, change roles, or remove a user.</p>
</div>""",
        unsafe_allow_html=True,
    )

    st.write("")

    users = get_all_users()
    current_user_id = st.session_state.user["id"]

    if not users:
        st.info("No users found.")
        return

    for u in users:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

            with col1:
                st.markdown(f"**{u['full_name']}**")
                st.caption(f"{u['email']} · @{u['username']}")

            with col2:
                st.caption("Role")
                st.write("🛡️ Admin" if u["role"] == "admin" else "👤 User")

            with col3:
                is_self = u["id"] == current_user_id
                is_default_admin = u["username"] == "admin"
                new_role = "user" if u["role"] == "admin" else "admin"
                label = "Demote to User" if u["role"] == "admin" else "Promote to Admin"

                if st.button(
                    label,
                    key=f"role_{u['id']}",
                    use_container_width=True,
                    disabled=is_self or is_default_admin,
                ):
                    update_user_role(u["id"], new_role)
                    st.success(f"{u['full_name']} is now {new_role}.")
                    st.rerun()

            with col4:
                is_self = u["id"] == current_user_id
                is_default_admin = u["username"] == "admin"

                if st.button(
                    "🗑️ Delete",
                    key=f"del_{u['id']}",
                    use_container_width=True,
                    disabled=is_self or is_default_admin,
                ):
                    delete_user(u["id"])
                    st.success(f"{u['full_name']} deleted.")
                    st.rerun()

    st.caption(
        "You can't demote/delete yourself or the built-in `admin` account — "
        "that's a safety rail to stop you locking yourself out."
    )