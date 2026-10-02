"""
Main application entrypoint for CineMatch AI - Movie Recommendation System.
Handles global session routing, sidebar navigation, theme injection, and page switching.
"""

import streamlit as st
from config import APP_NAME, APP_TAGLINE, APP_VERSION
from utils import load_css
from database import count_user_favorites

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="CineMatch AI - Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# LOAD GLOBAL STYLES
# ==========================================================

load_css()

# ==========================================================
# IMPORT PAGE MODULES
# ==========================================================

from pages.login import login_page
from pages.register import register_page
from pages.forgot_password import forgot_password_page
from pages.dashboard import dashboard_page
from pages.favorites import favorites_page
from pages.analytics import analytics_page
from pages.profile import profile_page


# ==========================================================
# SESSION STATE INITIALIZATION
# ==========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "current_menu" not in st.session_state:
    st.session_state.current_menu = "🏠 Dashboard"


# ==========================================================
# AUTHENTICATED USER ROUTING
# ==========================================================

if st.session_state.logged_in:

    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="font-size: 38px;">🎬</div>
                <h2 style="font-family: 'Outfit', sans-serif; font-size: 24px; margin: 0; background: linear-gradient(135deg, #FFFFFF, #A5B4FC); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {APP_NAME}
                </h2>
                <p style="font-size: 11px; color: #9CA3AF; margin: 2px 0 0 0;">v{APP_VERSION} • Production</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        user_fav_count = count_user_favorites(st.session_state.user_id)
        display_name = st.session_state.user_full_name or st.session_state.user or "User"
        initials = "".join([p[0].upper() for p in display_name.split()[:2]]) or "U"

        st.markdown(
            f"""
            <div class="sidebar-user-box">
                <div class="sidebar-user-avatar">
                    {initials}
                </div>
                <div style="font-weight: 700; font-size: 16px; color: #FFFFFF;">{display_name}</div>
                <div style="font-size: 13px; color: #A5B4FC;">@{st.session_state.user}</div>
                <div style="margin-top: 8px; font-size: 12px; color: #E2E8F0;">
                    ❤️ <b>{user_fav_count}</b> saved favorites
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        menu_items = [
            "🏠 Dashboard",
            "❤️ Favorites",
            "📊 Analytics",
            "👤 Profile",
            "🚪 Logout"
        ]

        # Handle menu selection
        default_index = 0
        if st.session_state.current_menu in menu_items:
            default_index = menu_items.index(st.session_state.current_menu)

        selected_menu = st.radio(
            "Navigation Menu",
            menu_items,
            index=default_index,
            label_visibility="collapsed"
        )
        st.session_state.current_menu = selected_menu

        st.markdown("---")
        st.caption(f"© 2026 {APP_NAME}. Powered by TF-IDF, Cosine Similarity & TMDB API.")

    # Route according to menu
    if selected_menu == "🏠 Dashboard":
        dashboard_page()

    elif selected_menu == "❤️ Favorites":
        favorites_page()

    elif selected_menu == "📊 Analytics":
        analytics_page()

    elif selected_menu == "👤 Profile":
        profile_page()

    elif selected_menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_full_name = None
        st.session_state.user_id = None
        st.session_state.page = "login"
        st.session_state.current_menu = "🏠 Dashboard"
        st.toast("Logged out successfully. See you soon! 👋")
        st.rerun()

# ==========================================================
# UNAUTHENTICATED ROUTING (LOGIN / REGISTER / FORGOT)
# ==========================================================

else:
    if st.session_state.page == "login":
        login_page()

    elif st.session_state.page == "register":
        register_page()

    elif st.session_state.page == "forgot":
        forgot_password_page()
