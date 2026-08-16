from pathlib import Path
import streamlit as st

CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "styles.css"


def load_css():
    if CSS_PATH.exists():
        with open(CSS_PATH, encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True,
            )


def require_login():
    """Redirect unauthenticated users."""
    if not st.session_state.get("authenticated", False):
        st.warning("🔒 Please log in to continue.")
        st.stop()


def require_admin():
    """
    Extra safety on top of require_login(): blocks anyone whose role
    isn't "admin". The sidebar navigation already only *shows*
    admin pages to admins, but this stops direct access too (e.g.
    someone bookmarking a URL or session state getting out of sync).
    """
    require_login()
    user = st.session_state.get("user")
    if not user or user.get("role") != "admin":
        st.error("🚫 This page is for administrators only.")
        st.stop()


def sidebar_user_panel():
    """Professional sidebar with user information."""
    user = st.session_state.get("user")

    with st.sidebar:
        st.markdown("## 🚀 TalentSphere AI")
        st.caption("Document Intelligence Platform")
        st.divider()

        if user:
            # Flush-left, no blank lines inside the HTML — a blank
            # line partway through breaks Streamlit's HTML parsing
            # and prints the rest as literal text.
            role_label = "ADMIN" if user.get("role") == "admin" else "USER"
            st.markdown(
                f"""<div class="user-card">
<div class="avatar">{user['full_name'][0].upper()}</div>
<div class="user-details">
<h4>{user['full_name']} <span style="font-size:11px;opacity:.75;">({role_label})</span></h4>
<p>{user['email']}</p>
</div>
</div>""",
                unsafe_allow_html=True,
            )

            st.write("")
            st.success("🟢 Logged In")
            st.divider()

            if st.button(
                "🚪 Logout",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()

        else:
            st.info("Please log in.")