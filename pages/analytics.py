"""
Analytics and Insights page module for Movie Recommendation System.
Renders interactive Plotly visual charts for dataset statistics, genre distributions, release timelines,
and community engagement metrics.
"""

import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from database import get_platform_stats, get_popular_searches, get_user_stats, get_user_favorites
from recommendation import load_metadata


def analytics_page():
    """Renders the comprehensive Analytics & Insights dashboard."""
    user_id = st.session_state.get("user_id")

    st.markdown(
        """
        <div class="hero-container" style="padding: 25px 20px; margin-bottom: 25px;">
            <span class="hero-badge">Data Science & Insights</span>
            <h1 class="hero-title" style="font-size: 36px !important;">📊 Cinema & Platform Analytics</h1>
            <p class="hero-subtitle" style="font-size: 15px !important;">
                Interactive data visualizations analyzing 45,000+ movies, genre patterns, rating trends, and community activity.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    metadata = load_metadata()
    platform_stats = get_platform_stats()
    user_stats = get_user_stats(user_id) if user_id else {}

    # ======================================================
    # PLATFORM HIGHLIGHT STATS
    # ======================================================
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Total Catalog Titles", f"{len(metadata):,}")
    with s2:
        st.metric("Community Searches", platform_stats.get("searches", 0))
    with s3:
        st.metric("Total Reviews & Comments", platform_stats.get("comments", 0))
    with s4:
        st.metric("Your Total Activity", user_stats.get("favorites", 0) + user_stats.get("likes", 0) + user_stats.get("searches", 0))

    st.write("")
    st.divider()

    # ======================================================
    # CHART SECTION 1: GENRE DISTRIBUTION & RELEASE DECADE
    # ======================================================
    row1_c1, row1_c2 = st.columns(2)

    with row1_c1:
        st.markdown("#### 🎭 Top Movie Genres in Catalog")
        
        # Calculate genre frequency
        genre_counts = {}
        for g_list in metadata["genre_list"]:
            for g in g_list:
                if g and g.strip():
                    genre_counts[g.strip()] = genre_counts.get(g.strip(), 0) + 1
        
        genre_df = pd.DataFrame(list(genre_counts.items()), columns=["Genre", "Count"]).sort_values(by="Count", ascending=False).head(12)
        
        if HAS_PLOTLY:
            fig_genre = px.bar(
                genre_df,
                x="Count",
                y="Genre",
                orientation="h",
                color="Count",
                color_continuous_scale="Viridis",
                title="Distribution of Top Genres",
                template="plotly_dark"
            )
            fig_genre.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F9FAFB"),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig_genre, use_container_width=True)
        else:
            st.bar_chart(genre_df.set_index("Genre"))

    with row1_c2:
        st.markdown("#### 📅 Movie Releases by Decade")
        
        valid_years = metadata[(metadata["release_year"] >= 1930) & (metadata["release_year"] <= 2024)].copy()
        valid_years["Decade"] = (valid_years["release_year"] // 10) * 10
        decade_counts = valid_years["Decade"].value_counts().sort_index().reset_index()
        decade_counts.columns = ["Decade", "Movies Count"]
        decade_counts["Decade"] = decade_counts["Decade"].astype(str) + "s"

        if HAS_PLOTLY:
            fig_decade = px.area(
                decade_counts,
                x="Decade",
                y="Movies Count",
                title="Cinema Production Trend by Decade",
                markers=True,
                template="plotly_dark",
                color_discrete_sequence=["#8B5CF6"]
            )
            fig_decade.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F9FAFB")
            )
            st.plotly_chart(fig_decade, use_container_width=True)
        else:
            st.area_chart(decade_counts.set_index("Decade"))

    st.divider()

    # ======================================================
    # CHART SECTION 2: RATING VS POPULARITY & MOST SEARCHED
    # ======================================================
    row2_c1, row2_c2 = st.columns(2)

    with row2_c1:
        st.markdown("#### ⭐ Rating vs. Popularity Scatter")
        sample_movies = metadata[(metadata["vote_count"] >= 100) & (metadata["vote_average"] > 0)].sample(min(300, len(metadata)))
        
        if HAS_PLOTLY:
            fig_scatter = px.scatter(
                sample_movies,
                x="vote_average",
                y="popularity",
                hover_name="title",
                color="vote_average",
                color_continuous_scale="Plasma",
                labels={"vote_average": "Rating (0-10)", "popularity": "Popularity Score"},
                title="Audience Score vs. Popularity Metric",
                template="plotly_dark"
            )
            fig_scatter.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F9FAFB")
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.scatter_chart(sample_movies[["vote_average", "popularity"]])

    with row2_c2:
        st.markdown("#### 🔥 Most Popular Community Search Queries")
        pop_searches = get_popular_searches(limit=8)
        if pop_searches:
            search_df = pd.DataFrame(pop_searches)
            if HAS_PLOTLY:
                fig_searches = px.pie(
                    search_df,
                    names="movie_title",
                    values="count",
                    title="Top Trending Searches by Users",
                    hole=0.45,
                    color_discrete_sequence=px.colors.sequential.Sunset
                )
                fig_searches.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#F9FAFB")
                )
                st.plotly_chart(fig_searches, use_container_width=True)
            else:
                st.dataframe(search_df, use_container_width=True)
        else:
            st.info("💡 As users search and explore movies, search trends will automatically populate here.")

    # ======================================================
    # PERSONAL TASTE INSIGHTS
    # ======================================================
    if user_id:
        st.divider()
        st.markdown("### 🧬 Your Personal CineMatch DNA")
        user_favs = get_user_favorites(user_id)
        if user_favs:
            user_genres = {}
            for f in user_favs:
                g_str = f.get("genre", "")
                for g in g_str.split(","):
                    if g.strip():
                        user_genres[g.strip()] = user_genres.get(g.strip(), 0) + 1
            if user_genres:
                user_genre_df = pd.DataFrame(list(user_genres.items()), columns=["Genre", "Count"]).sort_values(by="Count", ascending=False)
                if HAS_PLOTLY:
                    fig_user_pie = px.pie(
                        user_genre_df,
                        names="Genre",
                        values="Count",
                        title="Your Favorite Genres Breakdown",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_user_pie.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#F9FAFB")
                    )
                    st.plotly_chart(fig_user_pie, use_container_width=True)
                else:
                    st.bar_chart(user_genre_df.set_index("Genre"))
        else:
            st.info("Add movies to your Favorites to unlock personalized taste analytics and favorite genre breakdowns!")
