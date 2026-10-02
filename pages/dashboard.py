"""
Dashboard page module for Movie Recommendation System.
Features multi-tab search, trending/top-rated discovery, advanced hybrid filters,
instant AI recommendations, trailer links, reactions, ratings, and reviews.
"""

import streamlit as st
import pandas as pd
from recommendation import (
    recommend,
    get_movie_details,
    search_movie,
    get_all_genres,
    get_trending_movies,
    get_top_rated_movies,
    get_surprise_movie,
    fetch_movie_trailer,
    total_movies_count
)
from database import (
    get_platform_stats,
    save_search,
    add_favorite,
    remove_favorite,
    is_favorite,
    toggle_like,
    toggle_dislike,
    get_movie_user_reaction,
    get_movie_reaction_counts,
    save_movie_rating,
    get_user_movie_rating,
    get_movie_community_rating,
    add_movie_comment,
    get_movie_comments
)
from utils import render_genre_chips, get_safe_poster


def dashboard_page():
    """Renders the main dashboard interface."""
    user_id = st.session_state.get("user_id")
    user_name = st.session_state.get("user_full_name") or st.session_state.get("user", "Movie Fan")

    # ======================================================
    # HERO SECTION
    # ======================================================
    st.markdown(
        f"""
        <div class="hero-container">
            <span class="hero-badge">AI-Powered Cinema Intelligence</span>
            <h1 class="hero-title">Discover Your Next Favorite Movie</h1>
            <p class="hero-subtitle">
                Welcome back, <b>{user_name}</b>! Explore 45,000+ movies with personalized TF-IDF similarity, hybrid filters, and community reviews.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # LIVE PLATFORM METRICS
    # ======================================================
    stats = get_platform_stats()
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric("🎬 Movie Catalog", f"{total_movies_count():,}")
    with m_col2:
        st.metric("👤 Active Users", stats.get("users", 0))
    with m_col3:
        st.metric("❤️ Favorites Saved", stats.get("favorites", 0))
    with m_col4:
        st.metric("👍 Community Likes", stats.get("likes", 0))
    with m_col5:
        st.metric("⭐ Reviews & Ratings", stats.get("ratings", 0) + stats.get("comments", 0))

    st.write("")

    # ======================================================
    # TABS FOR DISCOVERY & SEARCH
    # ======================================================
    tab_search, tab_trending, tab_top_rated, tab_surprise = st.tabs([
        "🔍 AI Recommendation Search",
        "🔥 Trending Movies",
        "⭐ Top Rated Classics",
        "🎲 Surprise Me Pick"
    ])

    # ------------------------------------------------------
    # TAB 1: AI SEARCH & RECOMMENDATIONS
    # ------------------------------------------------------
    with tab_search:
        st.markdown("### 🎯 Find Movies & Generate AI Recommendations")
        
        search_col, btn_col = st.columns([3, 1])
        with search_col:
            keyword = st.text_input(
                "Search Movie Title",
                placeholder="Type movie name (e.g. Inception, Avatar, Toy Story, The Dark Knight)...",
                label_visibility="collapsed",
                key="dash_search_input"
            )

        selected_title = ""
        if keyword.strip():
            suggestions_df = search_movie(keyword.strip(), limit=15)
            if not suggestions_df.empty:
                # Format options with release year and rating for clear distinction
                display_options = []
                for _, row in suggestions_df.iterrows():
                    year_str = f" ({row['release_year']})" if row['release_year'] > 0 else ""
                    rating_str = f" ⭐ {row['vote_average']}" if row['vote_average'] > 0 else ""
                    display_options.append(f"{row['title']}{year_str}{rating_str}")
                
                selected_display = st.selectbox(
                    "Select Exact Match from Database:",
                    display_options,
                    key="dash_movie_select"
                )
                # Extract original title from selected display option
                selected_title = suggestions_df.iloc[display_options.index(selected_display)]["title"]
            else:
                st.info("💡 No exact match found in dataset. Try typing a partial name or popular title.")

        # Advanced Recommendation Filters
        with st.expander("⚙️ Advanced Recommendation Filters & Customization", expanded=False):
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                all_genres = ["All"] + get_all_genres()
                genre_filter = st.selectbox("Genre Filter", all_genres, index=0)
            with f_col2:
                min_rating = st.slider("Minimum Rating", min_value=0.0, max_value=10.0, value=0.0, step=0.5)
            with f_col3:
                year_range = st.slider("Release Year Range", min_value=1920, max_value=2025, value=(1970, 2025))
            with f_col4:
                top_n = st.selectbox("Recommendations Count", [5, 10, 15, 20], index=1)

        search_trigger = st.button("🚀 Get AI Recommendations", use_container_width=True, key="dash_rec_trigger")

        if search_trigger:
            if not selected_title and not keyword.strip():
                st.warning("⚠️ Please enter and select a movie name first.")
            else:
                target = selected_title if selected_title else keyword.strip()
                searched_movie, rec_df = recommend(
                    target,
                    top_n=top_n,
                    genre_filter=genre_filter,
                    min_rating=min_rating,
                    min_year=year_range[0],
                    max_year=year_range[1]
                )

                if searched_movie is None:
                    st.error("❌ Movie could not be found in recommendation model.")
                else:
                    st.session_state.current_selected_movie = searched_movie
                    st.session_state.current_recommendations = rec_df
                    if user_id:
                        save_search(user_id, searched_movie["title"])

        # Display Selected Movie & Recommendations if present in session state
        if st.session_state.get("current_selected_movie"):
            render_selected_movie_section(st.session_state.current_selected_movie, user_id)
            
            rec_df = st.session_state.get("current_recommendations")
            if rec_df is not None and not rec_df.empty:
                render_recommendations_section(rec_df, user_id)
            elif rec_df is not None and rec_df.empty:
                st.warning("⚠️ No recommendations matched your active filter criteria (e.g. genre or minimum rating). Try relaxing the filters.")

    # ------------------------------------------------------
    # TAB 2: TRENDING MOVIES
    # ------------------------------------------------------
    with tab_trending:
        st.markdown("### 🔥 Trending & Most Popular Movies")
        st.caption("Top popular movies curated from 45,000+ titles based on global viewership.")
        trending_list = get_trending_movies(limit=8)
        render_movie_grid_showcase(trending_list, user_id, key_prefix="trending")

    # ------------------------------------------------------
    # TAB 3: TOP RATED CLASSICS
    # ------------------------------------------------------
    with tab_top_rated:
        st.markdown("### ⭐ All-Time Top Rated Classics")
        st.caption("Critically acclaimed masterpieces with the highest audience score and substantial reviews.")
        top_rated_list = get_top_rated_movies(limit=8)
        render_movie_grid_showcase(top_rated_list, user_id, key_prefix="top_rated")

    # ------------------------------------------------------
    # TAB 4: SURPRISE ME
    # ------------------------------------------------------
    with tab_surprise:
        st.markdown("### 🎲 CineMatch Surprise Pick")
        st.caption("Feeling indecisive? Let our engine pick a hidden gem for your movie night!")
        if st.button("✨ Roll the Dice / Surprise Me!", key="dash_surprise_btn"):
            surprise_movie = get_surprise_movie()
            if surprise_movie:
                st.session_state.current_selected_movie = surprise_movie
                _, rec_df = recommend(surprise_movie["title"], top_n=8)
                st.session_state.current_recommendations = rec_df
                if user_id:
                    save_search(user_id, surprise_movie["title"])
                st.rerun()

        if st.session_state.get("current_selected_movie"):
            st.info(f"Currently viewing: **{st.session_state.current_selected_movie['title']}** (Switch to the AI Recommendation Search tab to see full details).")


# ==========================================================
# RENDER SELECTED MOVIE CARD
# ==========================================================

def render_selected_movie_section(movie: dict, user_id: int):
    """Renders the detailed hero card for the selected movie."""
    st.divider()
    st.markdown("## 🎥 Selected Movie")

    col_poster, col_info = st.columns([1, 2.3])

    with col_poster:
        poster_src = get_safe_poster(movie.get("poster"))
        st.image(poster_src, use_container_width=True)
        
        # Trailer Button
        trailer_url = fetch_movie_trailer(movie["title"], movie.get("release_year"))
        if trailer_url:
            st.link_button("▶️ Watch Official Trailer", trailer_url, use_container_width=True)

    with col_info:
        st.markdown(f"<div class='movie-title-large'>{movie['title']}</div>", unsafe_allow_html=True)
        
        # Badges row
        badges_html = f"""
        <div style="margin-bottom: 12px;">
            <span class="rating-badge">⭐ {movie['rating']:.1f} / 10 ({movie.get('vote_count', 0):,} votes)</span>
            <span style="color: #94A3B8; font-size: 14px; margin-right: 12px;">📅 {movie['release_date']}</span>
            {render_genre_chips(movie.get('genre_list', []))}
        </div>
        """
        st.markdown(badges_html, unsafe_allow_html=True)

        if movie.get("cast") and movie["cast"] != "N/A":
            st.markdown(f"**🎭 Starring:** `{movie['cast']}`")

        st.markdown("#### Overview")
        st.markdown(f"<p class='movie-overview-text'>{movie['overview']}</p>", unsafe_allow_html=True)

        # User Interaction Row: Favorite, Like, Dislike
        if user_id:
            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                fav_status = is_favorite(user_id, movie["title"])
                fav_label = "💔 Remove Favorite" if fav_status else "❤️ Add to Favorites"
                if st.button(fav_label, key=f"fav_sel_{movie['title']}", use_container_width=True):
                    if fav_status:
                        remove_favorite(user_id, movie["title"])
                        st.toast("Removed from Favorites")
                    else:
                        add_favorite(
                            user_id=user_id,
                            movie_title=movie["title"],
                            movie_id=movie.get("id", ""),
                            poster_path=movie.get("poster", ""),
                            rating=movie.get("rating", 0.0),
                            genre=movie.get("genres", "")
                        )
                        st.toast("Added to Favorites ❤️")
                    st.rerun()

            reaction = get_movie_user_reaction(user_id, movie["title"])
            counts = get_movie_reaction_counts(movie["title"])
            
            with act_col2:
                like_label = f"👍 Liked ({counts['likes']})" if reaction == "liked" else f"👍 Like ({counts['likes']})"
                if st.button(like_label, key=f"like_sel_{movie['title']}", use_container_width=True):
                    res = toggle_like(user_id, movie["title"])
                    st.toast("Liked movie 👍" if res == "liked" else "Like removed")
                    st.rerun()

            with act_col3:
                dislike_label = f"👎 Disliked ({counts['dislikes']})" if reaction == "disliked" else f"👎 Dislike ({counts['dislikes']})"
                if st.button(dislike_label, key=f"dislike_sel_{movie['title']}", use_container_width=True):
                    res = toggle_dislike(user_id, movie["title"])
                    st.toast("Disliked movie 👎" if res == "disliked" else "Dislike removed")
                    st.rerun()

            # Community Rating & Reviews Expander
            with st.expander("⭐ Rate & Write a Review", expanded=False):
                r_col1, r_col2 = st.columns([1, 2])
                with r_col1:
                    cur_rating = get_user_movie_rating(user_id, movie["title"]) or 5.0
                    user_star = st.slider("Your Rating (1 - 5 ⭐)", min_value=1.0, max_value=5.0, value=float(cur_rating), step=0.5, key=f"rate_slider_{movie['title']}")
                    if st.button("Save Rating ⭐", key=f"save_rate_{movie['title']}"):
                        save_movie_rating(user_id, movie["title"], user_star)
                        st.success(f"Rated {user_star} ⭐!")
                        st.rerun()

                with r_col2:
                    user_comment = st.text_area("Share your review with CineMatch community:", placeholder="What did you love or hate about this film?", key=f"comment_text_{movie['title']}")
                    if st.button("Post Review 💬", key=f"post_comment_{movie['title']}"):
                        if user_comment.strip():
                            add_movie_comment(user_id, movie["title"], user_comment)
                            st.success("Review posted successfully! 🎉")
                            st.rerun()
                        else:
                            st.warning("Please enter your thoughts before posting.")

                # Show existing community reviews
                comments = get_movie_comments(movie["title"], limit=5)
                if comments:
                    st.markdown("##### 💬 Recent Community Reviews")
                    for comm in comments:
                        st.markdown(f"**@{comm['username']}** ({comm['comment_time'][:10]}):")
                        st.markdown(f"> *{comm['comment']}*")
                        st.write("")


# ==========================================================
# RENDER RECOMMENDATIONS LIST
# ==========================================================

def render_recommendations_section(rec_df: pd.DataFrame, user_id: int):
    """Renders the recommended movies with similarity badges and interactive actions."""
    st.divider()
    st.markdown("## 🎬 Recommended Movies (Personalized Matches)")

    for idx, row in rec_df.iterrows():
        movie_det = get_movie_details(row["title"])
        if not movie_det:
            continue

        similarity_pct = float(row.get("similarity", 0.0)) * 100

        with st.container():
            col1, col2 = st.columns([1, 3.2])
            
            with col1:
                poster_img = get_safe_poster(movie_det.get("poster"))
                st.image(poster_img, use_container_width=True)

            with col2:
                st.markdown(f"<h3 style='color: #FFFFFF; font-family: Outfit; margin-bottom: 6px;'>{movie_det['title']}</h3>", unsafe_allow_html=True)
                
                # Badges row
                badges = f"""
                <div style="margin-bottom: 8px;">
                    <span class="match-score-badge">🎯 {similarity_pct:.1f}% Match</span>
                    <span class="rating-badge">⭐ {movie_det['rating']:.1f}</span>
                    <span style="color: #94A3B8; font-size: 13px; margin-right: 8px;">📅 {movie_det['release_date']}</span>
                    {render_genre_chips(movie_det.get('genre_list', []))}
                </div>
                """
                st.markdown(badges, unsafe_allow_html=True)

                st.progress(min(max(int(similarity_pct), 0), 100))

                st.markdown(f"<p style='color: #CBD5E1; font-size: 14px; line-height: 1.5;'>{movie_det['overview']}</p>", unsafe_allow_html=True)

                if user_id:
                    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)
                    
                    with btn_c1:
                        if st.button("🔍 Explore Similar", key=f"rec_explore_{idx}_{movie_det['title']}", use_container_width=True):
                            st.session_state.current_selected_movie = movie_det
                            _, new_recs = recommend(movie_det["title"], top_n=10)
                            st.session_state.current_recommendations = new_recs
                            save_search(user_id, movie_det["title"])
                            st.rerun()

                    with btn_c2:
                        fav = is_favorite(user_id, movie_det["title"])
                        if st.button("💔 Saved" if fav else "❤️ Favorite", key=f"rec_fav_{idx}_{movie_det['title']}", use_container_width=True):
                            if fav:
                                remove_favorite(user_id, movie_det["title"])
                                st.toast("Removed from Favorites")
                            else:
                                add_favorite(user_id, movie_det["title"], movie_det.get("id", ""), movie_det.get("poster", ""), movie_det.get("rating", 0.0), movie_det.get("genres", ""))
                                st.toast("Added to Favorites ❤️")
                            st.rerun()

                    with btn_c3:
                        reaction = get_movie_user_reaction(user_id, movie_det["title"])
                        if st.button("👍 Liked" if reaction == "liked" else "👍 Like", key=f"rec_like_{idx}_{movie_det['title']}", use_container_width=True):
                            toggle_like(user_id, movie_det["title"])
                            st.rerun()

                    with btn_c4:
                        trailer = fetch_movie_trailer(movie_det["title"], movie_det.get("release_year"))
                        if trailer:
                            st.link_button("▶️ Trailer", trailer, use_container_width=True)
                        else:
                            st.button("No Trailer", disabled=True, key=f"rec_notrail_{idx}", use_container_width=True)

            st.divider()


# ==========================================================
# SHOWCASE GRID (FOR TRENDING / TOP RATED)
# ==========================================================

def render_movie_grid_showcase(movies_list: list, user_id: int, key_prefix: str = "showcase"):
    """Renders a 4-column responsive grid for browsing movies."""
    if not movies_list:
        st.info("No movies found.")
        return

    cols = st.columns(4)
    for i, m in enumerate(movies_list):
        with cols[i % 4]:
            poster = get_safe_poster(m.get("poster"))
            st.image(poster, use_container_width=True)
            st.markdown(f"**{m['title']}**")
            st.caption(f"⭐ {m['rating']:.1f} • {m.get('release_date', 'N/A')[:4]}")
            
            if st.button("🚀 Recommend", key=f"{key_prefix}_rec_btn_{i}_{m['title']}", use_container_width=True):
                st.session_state.current_selected_movie = m
                _, rec_df = recommend(m["title"], top_n=10)
                st.session_state.current_recommendations = rec_df
                if user_id:
                    save_search(user_id, m["title"])
                st.toast(f"Generating recommendations for {m['title']}...")
                st.rerun()
            st.write("")
