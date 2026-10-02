"""
User Profile page module for Movie Recommendation System.
Handles account management, password change, user statistics, and search history viewer.
"""

import streamlit as st
from auth import get_user_by_id, update_user_profile, change_password
from database import get_user_stats, get_user_search_history, clear_user_search_history


def profile_page():
    """Renders the comprehensive user profile and settings page."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please sign in to view your profile.")
        return

    user_info = get_user_by_id(user_id)
    if not user_info:
        st.error("User profile could not be loaded.")
        return

    st.markdown(
        """
        <div class="hero-container" style="padding: 25px 20px; margin-bottom: 25px;">
            <span class="hero-badge">Account & Activity</span>
            <h1 class="hero-title" style="font-size: 36px !important;">👤 Member Profile</h1>
            <p class="hero-subtitle" style="font-size: 15px !important;">
                Manage your credentials, view your cinema interaction history, and update preferences.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # USER SUMMARY CARD & ACTIVITY STATS
    # ======================================================
    stats = get_user_stats(user_id)
    
    col_avatar, col_details = st.columns([1, 2.5])

    with col_avatar:
        initials = "".join([part[0].upper() for part in user_info['full_name'].split()[:2]]) or "U"
        st.markdown(
            f"""
            <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 20px; padding: 24px; text-align: center;">
                <div class="sidebar-user-avatar" style="width: 80px; height: 80px; font-size: 34px;">
                    {initials}
                </div>
                <h3 style="color: #FFFFFF; margin-bottom: 4px;">{user_info['full_name']}</h3>
                <p style="color: #A5B4FC; font-weight: 600; margin-bottom: 6px;">@{user_info['username']}</p>
                <span style="display: inline-block; background: rgba(99, 102, 241, 0.2); color: #C7D2FE; font-size: 12px; padding: 4px 10px; border-radius: 12px;">
                    Member since {user_info.get('created_at', '')[:10]}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_details:
        st.markdown("#### 📈 Your Activity Highlights")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("❤️ Favorites Saved", stats.get("favorites", 0))
        with s2:
            st.metric("👍 Likes Given", stats.get("likes", 0))
        with s3:
            st.metric("⭐ Ratings & Reviews", stats.get("ratings", 0) + stats.get("comments", 0))

        st.write("")
        st.markdown(f"**📧 Email:** `{user_info['email']}`")
        st.markdown(f"**🔍 Total Movie Searches:** `{stats.get('searches', 0)}`")

    st.divider()

    # ======================================================
    # TABS FOR SETTINGS & SEARCH HISTORY
    # ======================================================
    tab_history, tab_edit, tab_security = st.tabs([
        "📜 Search History",
        "✏️ Edit Profile Info",
        "🔒 Change Password"
    ])

    # ------------------------------------------------------
    # TAB 1: SEARCH HISTORY
    # ------------------------------------------------------
    with tab_history:
        st.markdown("#### 🕒 Your Recent Movie Searches")
        history = get_user_search_history(user_id, limit=20)
        
        if history:
            h_col1, h_col2 = st.columns([3, 1])
            with h_col2:
                if st.button("🗑️ Clear Search History", key="clear_hist_btn", use_container_width=True):
                    clear_user_search_history(user_id)
                    st.toast("Search history cleared!")
                    st.rerun()

            for item in history:
                st.markdown(f"- 🎬 **{item['movie_title']}** — <span style='color: #9CA3AF; font-size: 13px;'>{item['search_time']}</span>", unsafe_allow_html=True)
        else:
            st.info("No recent search history found. Start exploring movies from the Dashboard!")

    # ------------------------------------------------------
    # TAB 2: EDIT PROFILE
    # ------------------------------------------------------
    with tab_edit:
        st.markdown("#### ✏️ Update Profile Information")
        with st.form("edit_profile_form"):
            new_name = st.text_input("Full Name", value=user_info["full_name"])
            new_email = st.text_input("Email Address", value=user_info["email"])
            submit_profile = st.form_submit_button("Save Changes 💾")

            if submit_profile:
                success, msg = update_user_profile(user_id, new_name, new_email)
                if success:
                    st.session_state.user_full_name = new_name
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    # ------------------------------------------------------
    # TAB 3: SECURITY / CHANGE PASSWORD
    # ------------------------------------------------------
    with tab_security:
        st.markdown("#### 🔒 Update Your Password")
        with st.form("change_password_form"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password (minimum 6 characters)", type="password")
            confirm_new_pw = st.text_input("Confirm New Password", type="password")
            submit_pw = st.form_submit_button("Update Password 🔄")

            if submit_pw:
                if not current_pw or not new_pw or not confirm_new_pw:
                    st.warning("Please fill in all password fields.")
                elif new_pw != confirm_new_pw:
                    st.error("New passwords do not match.")
                else:
                    success, msg = change_password(user_id, current_pw, new_pw)
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
