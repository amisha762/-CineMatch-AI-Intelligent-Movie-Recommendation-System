"""
Configuration module for Movie Recommendation System.
Centralizes paths, environment variables, API keys, and app constants.
"""

import os
from pathlib import Path
import streamlit as st

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Data Paths
DATA_DIR = BASE_DIR
MOVIES_PKL_PATH = BASE_DIR / "movies.pkl"
TFIDF_MATRIX_PATH = BASE_DIR / "tfidf_matrix.pkl"
TFIDF_VECTORIZER_PATH = BASE_DIR / "tfidf_vectorizer.pkl"
METADATA_CSV_PATH = BASE_DIR / "movie_recommendation_cleaned_dataset_v2.csv"
DATABASE_PATH = BASE_DIR / "movie_recommendation.db"

# Assets Directory (handles both 'assets' and 'assests' for backward compatibility)
ASSETS_DIR = BASE_DIR / "assets"
if not ASSETS_DIR.exists():
    ASSETS_DIR = BASE_DIR / "assests"

DEFAULT_POSTER_PATH = ASSETS_DIR / "default_poster.jpg"

# TMDB API Key resolution
# 1. Streamlit Secrets (for Streamlit Cloud)
# 2. Environment Variable
# 3. Fallback Default Key
def get_tmdb_api_key() -> str:
    try:
        if hasattr(st, "secrets") and "TMDB_API_KEY" in st.secrets:
            return st.secrets["TMDB_API_KEY"]
    except Exception:
        pass
    return os.getenv("TMDB_API_KEY", "3122f5f88b8b0f31282f2af4e9ec16da")

TMDB_API_KEY = get_tmdb_api_key()
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_ORIGINAL_IMAGE_URL = "https://image.tmdb.org/t/p/original"

# App Metadata
APP_NAME = "CineMatch AI"
APP_TAGLINE = "AI-Powered Personalized Movie Recommendation Platform"
APP_VERSION = "2.0.0"
