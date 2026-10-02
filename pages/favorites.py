"""
Favorites and Watchlist page module for Movie Recommendation System.
Allows users to view, search, filter, remove, and get recommendations from their saved movies.
"""

import streamlit as st
from database import get_user_favorites, remove_favorite, save_search
from recommendation import get_movie_details, recommend, fetch_movie_trailer
from utils import get_safe_poster, render_genre_chips


def favorites_page():
    """Renders the user's personal favorites and watchlist."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please sign in to view your favorites.")
        return

    st.markdown(
        """
        <div class="hero-container" style="padding: 25px 20px; margin-bottom: 25px;">
            <span class="hero-badge">Your Cinema Collection</span>
            <h1 class="hero-title" style="font-size: 36px !important;">❤️ My Favorites & Watchlist</h1>
            <p class="hero-subtitle" style="font-size: 15px !important;">
                Manage your curated list of favorite films and find personalized matches from them.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    favorites = get_user_favorites(user_id)

    if not favorites:
        st.info("🍿 You haven't added any movies to your favorites yet! Go to the **Dashboard**, discover great movies, and click **❤️ Favorite** to save them here.")
        if st.button("🎬 Go to Dashboard", key="fav_empty_goto_dash"):
            st.session_state.current_menu = "🏠 Dashboard"
            st.rerun()
        return

    st.markdown(f"#### 📚 Total Saved: **{len(favorites)}** Movies")

    # Filters and Search inside Favorites
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        search_filter = st.text_input("Filter your favorites by title:", placeholder="Type to filter...", key="fav_search_filter")
    with f_col2:
        sort_by = st.selectbox("Sort By", ["Recently Added", "Highest Rating", "Title (A-Z)"], key="fav_sort_select")

    # Apply search filter
    filtered_favs = favorites
    if search_filter.strip():
        filtered_favs = [f for f in filtered_favs if search_filter.strip().lower() in f["movie_title"].lower()]

    # Apply sorting
    if sort_by == "Highest Rating":
        filtered_favs = sorted(filtered_favs, key=lambda x: x.get("rating", 0.0), reverse=True)
    elif sort_by == "Title (A-Z)":
        filtered_favs = sorted(filtered_favs, key=lambda x: x["movie_title"].lower())

    st.write("")

    # Grid Display (3 columns)
    cols = st.columns(3)
    for idx, fav in enumerate(filtered_favs):
        title = fav["movie_title"]
        movie_det = get_movie_details(title)

        with cols[idx % 3]:
            with st.container():
                st.markdown("<div class='movie-card-container'>", unsafe_allow_html=True)
                
                poster = get_safe_poster(movie_det.get("poster") if movie_det else fav.get("poster_path"))
                st.image(poster, use_container_width=True)
                
                rating_val = movie_det["rating"] if movie_det else fav.get("rating", 0.0)
                genres_val = movie_det.get("genre_list", []) if movie_det else [fav.get("genre", "")]

                st.markdown(f"### {title}")
                st.markdown(f"⭐ **Rating:** {rating_val:.1f} / 10")
                st.markdown(f"📅 **Added:** `{fav.get('added_time', '')[:10]}`")
                
                if genres_val:
                    st.markdown(render_genre_chips(genres_val), unsafe_allow_html=True)

                st.write("")
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("🚀 Recommend", key=f"fav_rec_btn_{idx}_{title}", use_container_width=True):
                        if movie_det:
                            st.session_state.current_selected_movie = movie_det
                            _, rec_df = recommend(title, top_n=10)
                            st.session_state.current_recommendations = rec_df
                            save_search(user_id, title)
                            st.session_state.current_menu = "🏠 Dashboard"
                            st.toast(f"Generated recommendations for {title}!")
                            st.rerun()
                with b2:
                    if st.button("🗑️ Remove", key=f"fav_del_btn_{idx}_{title}", use_container_width=True):
                        remove_favorite(user_id, title)
                        st.toast(f"Removed {title} from favorites")
                        st.rerun()

                # Trailer Link
                trailer = fetch_movie_trailer(title)
                if trailer:
                    st.link_button("▶️ Watch Trailer", trailer, use_container_width=True)

                st.markdown("</div>", unsafe_allow_html=True)
                st.write("")
