"""
Forgot Password page module for Movie Recommendation System.
"""

import streamlit as st
from auth import reset_password


def forgot_password_page():
    """Renders password recovery page."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px; margin-bottom: 25px;">
            <div style="font-size: 54px; margin-bottom: 10px;">🔐</div>
            <h1 class="hero-title" style="font-size: 40px !important;">Account Recovery</h1>
            <p class="hero-subtitle" style="font-size: 16px !important;">
                Reset your CineMatch AI account password
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
                <h2 class="auth-header-title">Reset Password</h2>
                <p class="auth-header-subtitle">Enter your registered email and choose a new password</p>
            """,
            unsafe_allow_html=True
        )

        email = st.text_input("Registered Email", placeholder="Enter your email address", key="reset_email")
        new_password = st.text_input("New Password", type="password", placeholder="Minimum 6 characters", key="reset_pass")
        confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password", key="reset_confirm")

        st.write("")
        reset_btn = st.button("🔄 Update Password", use_container_width=True, key="reset_submit_btn")
        back_btn = st.button("⬅ Back to Login", use_container_width=True, key="reset_back_btn")

        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # ACTIONS
    # ======================================================

    if reset_btn:
        if not email.strip() or not new_password.strip() or not confirm_password.strip():
            st.warning("⚠️ Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("❌ Passwords do not match.")
        elif len(new_password) < 6:
            st.warning("⚠️ Password must be at least 6 characters long.")
        else:
            success, msg = reset_password(email, new_password)
            if success:
                st.success(f"✅ {msg}")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    if back_btn:
        st.session_state.page = "login"
        st.rerun()