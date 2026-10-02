"""
Login page module for Movie Recommendation System.
"""

import streamlit as st
from auth import login_user, register_user


def login_page():
    """Renders the login page with sleek glassmorphic UI."""
    
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px; margin-bottom: 25px;">
            <div style="font-size: 54px; margin-bottom: 10px;">🎬</div>
            <h1 class="hero-title" style="font-size: 40px !important;">CineMatch AI</h1>
            <p class="hero-subtitle" style="font-size: 16px !important;">
                Next-Generation Intelligent Movie Discovery & Recommendation
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    _, center_col, _ = st.columns([1, 1.8, 1])

    with center_col:
        st.markdown(
            """
            <div class="auth-wrapper">
                <h2 class="auth-header-title">Welcome Back</h2>
                <p class="auth-header-subtitle">Sign in to your account to get personalized recommendations</p>
            """,
            unsafe_allow_html=True
        )

        username_or_email = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_user_input"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_pass_input"
        )

        st.write("")
        login_btn = st.button("🚀 Sign In", use_container_width=True, key="login_submit_btn")

        st.markdown(
            """
            <div style="text-align: center; margin: 15px 0; color: #6B7280; font-size: 13px;">
                ─── OR QUICK DEMO ACCESS ───
            </div>
            """,
            unsafe_allow_html=True
        )

        demo_col1, demo_col2 = st.columns(2)
        with demo_col1:
            demo_login = st.button("⚡ Demo User", use_container_width=True, key="demo_login_btn")
        with demo_col2:
            new_acc_btn = st.button("📝 Register", use_container_width=True, key="goto_register_btn")

        forgot_btn = st.button("🔑 Forgot Password?", use_container_width=True, key="goto_forgot_btn")

        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # ACTIONS
    # ======================================================

    if login_btn:
        if not username_or_email.strip() or not password.strip():
            st.error("⚠️ Please enter both username/email and password.")
        else:
            user = login_user(username_or_email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user["username"]
                st.session_state.user_full_name = user["full_name"]
                st.session_state.user_id = user["user_id"]
                st.session_state.page = "dashboard"
                st.toast(f"Welcome back, {user['full_name']}! 👋")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please verify your username/password.")

    # Demo Quick Login
    if demo_login:
        # Create demo user if not existing
        register_user("Demo Explorer", "demouser", "demo@cinematch.ai", "demo12345")
        user = login_user("demouser", "demo12345")
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user["username"]
            st.session_state.user_full_name = user["full_name"]
            st.session_state.user_id = user["user_id"]
            st.session_state.page = "dashboard"
            st.toast("Logged in as Demo User 🍿")
            st.rerun()

    if new_acc_btn:
        st.session_state.page = "register"
        st.rerun()

    if forgot_btn:
        st.session_state.page = "forgot"
        st.rerun()