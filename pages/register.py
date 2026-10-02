"""
Registration page module for Movie Recommendation System.
"""

import streamlit as st
from auth import register_user


def register_page():
    """Renders the registration page."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px; margin-bottom: 25px;">
            <div style="font-size: 54px; margin-bottom: 10px;">🎬</div>
            <h1 class="hero-title" style="font-size: 40px !important;">Join CineMatch AI</h1>
            <p class="hero-subtitle" style="font-size: 16px !important;">
                Create your account to unlock curated AI recommendations & personal watchlist
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
                <h2 class="auth-header-title">Create Account</h2>
                <p class="auth-header-subtitle">Fill in your details below to get started</p>
            """,
            unsafe_allow_html=True
        )

        full_name = st.text_input("Full Name", placeholder="e.g. Alex Johnson", key="reg_name")
        email = st.text_input("Email Address", placeholder="e.g. alex@example.com", key="reg_email")
        username = st.text_input("Username", placeholder="e.g. alexj", key="reg_user")
        password = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")

        st.write("")
        create_btn = st.button("✨ Create Account", use_container_width=True, key="reg_submit_btn")
        back_btn = st.button("⬅ Back to Login", use_container_width=True, key="reg_back_btn")

        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # ACTIONS
    # ======================================================

    if create_btn:
        if not full_name.strip() or not email.strip() or not username.strip() or not password.strip():
            st.warning("⚠️ Please fill in all fields.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match.")
        elif len(password) < 6:
            st.warning("⚠️ Password must be at least 6 characters long.")
        else:
            success, msg = register_user(full_name, username, email, password)
            if success:
                st.success("🎉 Account created successfully! Please sign in.")
                st.balloons()
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    if back_btn:
        st.session_state.page = "login"
        st.rerun()