"""
Utility functions module for Movie Recommendation System.
Provides styling injectors, UI component renderers, and formatters.
"""

import os
import streamlit as st
from config import BASE_DIR, DEFAULT_POSTER_PATH


def load_css() -> None:
    """Loads and injects the global style.css file."""
    css_path = BASE_DIR / "styles" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ style.css not found.")


def render_genre_chips(genres_list) -> str:
    """Renders HTML badge chips for movie genres."""
    if not genres_list:
        return "<span class='genre-chip'>Unknown</span>"
    if isinstance(genres_list, str):
        genres_list = [g.strip() for g in genres_list.split(",") if g.strip()]
    
    html = ""
    for genre in genres_list[:4]:
        html += f"<span class='genre-chip'>{genre}</span>"
    return html


def get_safe_poster(poster_url: str) -> str:
    """Returns valid poster URL or local default poster image."""
    if poster_url and str(poster_url).strip() and str(poster_url) != "nan":
        return poster_url
    if DEFAULT_POSTER_PATH.exists():
        return str(DEFAULT_POSTER_PATH)
    return "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=400"