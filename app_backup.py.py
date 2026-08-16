"""
TalentSphere AI
Modern Authentication + Dashboard
"""

import streamlit as st

from src.auth import (
    init_db,
    create_user,
    verify_user,
)

from src.auth_ui import (
    load_css,
    sidebar_user_panel,
)

st.set_page_config(
    page_title="TalentSphere AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Initialize
# -----------------------------
init_db()
load_css()

# -----------------------------
# Session State
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "remember" not in st.session_state:
    st.session_state.remember = False

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

if "login_type" not in st.session_state:
    st.session_state.login_type = None


# =========================================================
# LOGIN / SIGNUP
# =========================================================

def show_auth_screen():

    left, right = st.columns([1.25, 1])

    # ---------------- LEFT PANEL (pure branding, no widgets — safe as a plain div) ----------------
    with left:
        st.markdown(
            """
<div class="login-left">
<h1>🚀 TalentSphere AI</h1>
<h3>Your Intelligent Document Assistant</h3>
<p>
✔ Upload PDF Documents<br><br>
✔ Semantic AI Search<br><br>
✔ ChromaDB Vector Database<br><br>
✔ Fast Document Retrieval<br><br>
✔ AI Powered Knowledge Base
</p>
<br>
<img src="https://img.icons8.com/fluency/240/artificial-intelligence.png" width="220">
</div>
""",
            unsafe_allow_html=True,
        )

    # ---------------- RIGHT PANEL ----------------
    # Everything here (heading + toggle + form) sits inside ONE real
    # bordered container, so it's actually boxed together — a plain
    # <div> can't wrap real widgets like buttons and forms.
    with right:
        with st.container(border=True):

            st.markdown(
                """<h2 style="text-align:center;">Welcome Back 👋</h2>
<p style="text-align:center;color:#6b7280;">Login to continue</p>""",
                unsafe_allow_html=True,
            )

            # ================= LOGIN / SIGNUP TOGGLE =================
            # (Just one toggle row now — the old code had a second,
            # separate Admin/User row underneath this one, with a
            # button also labeled "User Login" doing something
            # different. That's gone; roles aren't supported by the
            # database yet, so it can't work correctly right now.)
            st.markdown("### Select Login Type")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "👨‍💼 Admin Login",
                    use_container_width=True,
                ):
                    st.session_state.login_type = "admin"
                    st.session_state.auth_page = "login"
                    st.rerun()

            with col2:
                if st.button(
                    "👤 User Login",
                    use_container_width=True,
                ):
                    st.session_state.login_type = "user"
                    st.session_state.auth_page = "login"
                    st.rerun()

            st.write("")

            # ================= LOGIN =================
            # Show nothing until login type is selected
            if st.session_state.login_type is None:
                st.info("Select Admin Login or User Login to continue.")

            elif st.session_state.auth_page == "login":

                if st.session_state.login_type == "admin":
                    st.subheader("👨‍💼 Administrator Login")
                else:
                    st.subheader("👤 User Login")
                with st.form("login_form"):
                    username = st.text_input("👤 Username or Email")
                    password = st.text_input("🔒 Password", type="password")
                    remember = st.checkbox("Remember Me")
                    login = st.form_submit_button("Login", use_container_width=True)

                if login:
                    user = verify_user(username, password)

                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.remember = remember
                        st.success(f"Welcome back, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                if st.session_state.login_type == "user":

                    st.divider()

                    if st.button(
                        "📝 Create Account",
                        use_container_width=True,
                    ):
                        st.session_state.auth_page = "signup"
                        st.rerun()

            # ================= SIGN UP =================
            else:

                with st.form("signup_form"):
                    fullname = st.text_input("Full Name")
                    gender = st.selectbox(
                        "Gender",
                        ["Female", "Male", "Non-binary", "Prefer not to say"],
                    )
                    email = st.text_input("Email")
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    confirm = st.text_input("Confirm Password", type="password")
                    signup = st.form_submit_button("Create Account", use_container_width=True)

                if signup:
                    if password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        success, message = create_user(fullname, gender, email, username, password)
                        if success:
                            st.success(message)
                            st.session_state.auth_page = "login"
                            st.rerun()
                        else:
                            st.error(message)

                st.write("")
                if st.button("← Back to Login", use_container_width=True):
                    st.session_state.auth_page = "login"
                    st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

def show_dashboard():

    from src.vectorstore import stats
    from src.ui import dashboard_banner, metric_tile, footer

    sidebar_user_panel()

    user = st.session_state.user
    index = stats()

    # ---------------- Hero Banner ----------------
    dashboard_banner(user["full_name"])

    st.write("")

    # ---------------- Metrics ----------------
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_tile("📄 Documents", index["sources"])
    with c2:
        metric_tile("🧩 Chunks", index["total_chunks"])
    with c3:
        metric_tile("🤖 AI Model", "BGE Large")

    st.write("")
    st.markdown("## 🚀 Workspace")
    st.write("")

    # ---------------- Main Layout ----------------
    left, right = st.columns([2.3, 1])

    # =====================================================
    # LEFT SIDE
    # =====================================================
    with left:

        upload_col, search_col = st.columns(2)

        # Upload Card — heading + button share one real box
        with upload_col:
            with st.container(border=True):
                st.markdown(
                    """<h2>📤 Upload Documents</h2>
<p>Upload one or multiple PDF files to build your AI knowledge base.</p>""",
                    unsafe_allow_html=True,
                )
                if st.button("Open Upload", use_container_width=True, key="upload_button"):
                    st.switch_page("pages/1_📥_Ingest.py")

        # Search Card — same pattern
        with search_col:
            with st.container(border=True):
                st.markdown(
                    """<h2>🤖 AI Search</h2>
<p>Search your uploaded documents using natural language.</p>""",
                    unsafe_allow_html=True,
                )
                if st.button("Open Search", use_container_width=True, key="search_button"):
                    st.switch_page("pages/2_🔍_Search.py")

        st.write("")
        st.markdown("## 📚 Indexed Documents")
        st.write("")

        if index["source_names"]:
            for file in index["source_names"]:
                st.markdown(f'<div class="document-card">📄 {file}</div>', unsafe_allow_html=True)
        else:
            st.info("No documents uploaded yet.")

    # =====================================================
    # RIGHT SIDE — profile card, one real box
    # =====================================================
    with right:
        with st.container(border=True):
            st.markdown('<div class="profile-card"><h2>👤 Profile</h2></div>', unsafe_allow_html=True)

            st.write(f"**Name**  \n{user['full_name']}")
            st.write(f"**Email**  \n{user['email']}")
            st.write(f"**Username**  \n{user['username']}")

            st.write("")
            st.markdown("### 📈 Statistics")
            st.info(f"📄 Documents : {index['sources']}")
            st.info(f"🧩 Chunks : {index['total_chunks']}")
            st.success("🟢 System Online")
            # (No Logout button here — the sidebar already has one,
            # visible on every page.)

    st.write("")
    footer()


# =========================================================
# MAIN ROUTER
# =========================================================

if not st.session_state.authenticated:

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"]{ display:none; }
        header{ visibility:hidden; }
        footer{ visibility:hidden; }
        #MainMenu{ visibility:hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    show_auth_screen()

else:
    show_dashboard()