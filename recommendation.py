"""
Recommendation engine module for Movie Recommendation System.
Handles TF-IDF cosine similarity calculations, metadata parsing, TMDB API poster/trailer integration,
hybrid filtering (genre, rating, release year), and discovery modes (Trending, Top Rated, Surprise Me).
"""

import ast
import random
import os
from typing import Tuple, Optional, List, Dict, Any
import pandas as pd
import numpy as np
import pickle
import requests
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    MOVIES_PKL_PATH,
    TFIDF_MATRIX_PATH,
    METADATA_CSV_PATH,
    TMDB_API_KEY,
    TMDB_IMAGE_BASE_URL,
    DEFAULT_POSTER_PATH
)


# ==========================================================
# CACHED DATA LOADERS
# ==========================================================

@st.cache_resource(show_spinner="Loading Recommendation Models...")
def load_models():
    """Loads movies dataframe and TF-IDF similarity matrix."""
    with open(MOVIES_PKL_PATH, "rb") as f:
        movies_df = pickle.load(f)

    with open(TFIDF_MATRIX_PATH, "rb") as f:
        tfidf_mat = pickle.load(f)

    return movies_df, tfidf_mat


@st.cache_data(show_spinner="Loading Movie Metadata...", ttl=3600*12)
def load_metadata() -> pd.DataFrame:
    """Loads and preprocesses movie metadata CSV."""
    df = pd.read_csv(METADATA_CSV_PATH, low_memory=False)

    df["title"] = df["title"].fillna("").astype(str)
    df["title_clean"] = df["title"].str.strip().str.lower()
    df["overview"] = df["overview"].fillna("Overview not available.")
    df["genres"] = df["genres"].fillna("[]")
    df["release_date"] = df["release_date"].fillna("Unknown")
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0.0)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0.0)
    df["poster_path"] = df["poster_path"].fillna("")
    
    # Extract release year safely
    df["release_year"] = df["release_date"].astype(str).str.extract(r"(\d{4})")[0].fillna("0").astype(int)

    # Parse and clean genres into a readable list and string
    def clean_genre_list(genre_val):
        if not genre_val or pd.isna(genre_val):
            return []
        try:
            parsed = ast.literal_eval(str(genre_val))
            if isinstance(parsed, list):
                return [str(g).strip() for g in parsed if g]
        except Exception:
            pass
        cleaned = str(genre_val).replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        return [g.strip() for g in cleaned.split(",") if g.strip()]

    df["genre_list"] = df["genres"].apply(clean_genre_list)
    df["genre_str"] = df["genre_list"].apply(lambda g_list: ", ".join(g_list) if g_list else "Unknown")

    # Clean Cast
    def clean_cast_list(cast_val):
        if not cast_val or pd.isna(cast_val):
            return []
        try:
            parsed = ast.literal_eval(str(cast_val))
            if isinstance(parsed, list):
                # Add spacing to PascalCase names if needed (e.g. TomHanks -> Tom Hanks)
                res = []
                for c in parsed[:5]:
                    c_str = str(c).strip()
                    res.append(c_str)
                return res
        except Exception:
            pass
        return []

    df["cast_list"] = df["cast"].apply(clean_cast_list) if "cast" in df.columns else [[]] * len(df)
    df["cast_str"] = df["cast_list"].apply(lambda c_list: ", ".join(c_list) if c_list else "N/A")

    # Drop duplicate titles to ensure 1-1 mapping
    df = df.drop_duplicates(subset="title_clean").reset_index(drop=True)
    return df


# Load data once
movies, tfidf_matrix = load_models()
metadata = load_metadata()


# ==========================================================
# SEARCH & AUTOCOMPLETE
# ==========================================================

def search_movie(keyword: str, limit: int = 15) -> pd.DataFrame:
    """Searches metadata for matching movie titles with exact matches prioritized."""
    keyword_clean = keyword.strip().lower()
    if not keyword_clean:
        return pd.DataFrame(columns=["title", "release_year", "vote_average", "genre_str"])

    # Prefix match or substring match
    mask = metadata["title_clean"].str.contains(keyword_clean, regex=False, na=False)
    results = metadata[mask][["title", "release_year", "vote_average", "genre_str"]].copy()

    if results.empty:
        return results

    # Sort: Exact match first, then starts with keyword, then popularity
    results["exact_match"] = results["title"].str.lower() == keyword_clean
    results["starts_with"] = results["title"].str.lower().str.startswith(keyword_clean)

    results = results.sort_values(
        by=["exact_match", "starts_with", "vote_average"],
        ascending=[False, False, False]
    )

    return results.head(limit)


def get_all_genres() -> List[str]:
    """Returns sorted unique genres from the dataset."""
    unique_genres = set()
    for g_list in metadata["genre_list"]:
        for g in g_list:
            if g and g.strip():
                unique_genres.add(g.strip())
    return sorted(list(unique_genres))


# ==========================================================
# TMDB API ENHANCEMENTS (POSTERS & TRAILERS)
# ==========================================================

@st.cache_data(show_spinner=False, ttl=3600*24)
def fetch_tmdb_poster(movie_title: str, year: Optional[int] = None) -> Optional[str]:
    """Fetches high-res poster from TMDB API search if missing in local dataset."""
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": movie_title,
        }
        if year and year > 1900:
            params["year"] = str(year)

        response = requests.get(url, params=params, timeout=4)
        if response.status_code == 200:
            results = response.json().get("results", [])
            for res in results:
                if res.get("poster_path"):
                    return f"{TMDB_IMAGE_BASE_URL}{res['poster_path']}"
    except Exception:
        pass
    return None


@st.cache_data(show_spinner=False, ttl=3600*24)
def fetch_movie_trailer(movie_title: str, year: Optional[int] = None) -> Optional[str]:
    """Fetches YouTube trailer key or embed URL via TMDB."""
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": movie_title}
        if year and year > 1900:
            params["year"] = str(year)

        response = requests.get(url, params=params, timeout=4)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                tmdb_id = results[0]["id"]
                vid_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
                vid_resp = requests.get(vid_url, params={"api_key": TMDB_API_KEY}, timeout=4)
                if vid_resp.status_code == 200:
                    videos = vid_resp.json().get("results", [])
                    for vid in videos:
                        if vid.get("site") == "YouTube" and vid.get("type") in ["Trailer", "Teaser"]:
                            return f"https://www.youtube.com/watch?v={vid.get('key')}"
    except Exception:
        pass
    return None


# ==========================================================
# MOVIE DETAILS RETRIEVAL
# ==========================================================

def get_movie_details(movie_title: str) -> Optional[Dict[str, Any]]:
    """Retrieves full details for a given movie title."""
    title_clean = str(movie_title).strip().lower()
    
    # 1. Exact match
    match = metadata[metadata["title_clean"] == title_clean]
    
    # 2. Prefix match fallback
    if match.empty:
        match = metadata[metadata["title_clean"].str.startswith(title_clean)]
        
    # 3. Substring match fallback
    if match.empty:
        match = metadata[metadata["title_clean"].str.contains(title_clean, regex=False, na=False)]

    if match.empty:
        return None

    row = match.iloc[0]

    # Poster resolution: Local dataset poster_path first -> TMDB search -> Default
    poster_url = None
    raw_poster = str(row.get("poster_path", "")).strip()
    if raw_poster and raw_poster != "nan":
        if raw_poster.startswith("http"):
            poster_url = raw_poster
        elif raw_poster.startswith("/"):
            poster_url = f"{TMDB_IMAGE_BASE_URL}{raw_poster}"
    
    if not poster_url:
        poster_url = fetch_tmdb_poster(row["title"], row.get("release_year"))

    # Parse overview safely
    overview_text = str(row.get("overview", "Overview not available."))
    try:
        if overview_text.startswith("[") and overview_text.endswith("]"):
            parsed_overview = ast.literal_eval(overview_text)
            if isinstance(parsed_overview, list):
                overview_text = " ".join(parsed_overview)
    except Exception:
        pass

    return {
        "id": str(row.get("id", "")),
        "title": row["title"],
        "overview": overview_text,
        "rating": float(row.get("vote_average", 0.0)),
        "vote_count": int(row.get("vote_count", 0)),
        "release_date": str(row.get("release_date", "Unknown")),
        "release_year": int(row.get("release_year", 0)),
        "genres": row.get("genre_str", "Unknown"),
        "genre_list": row.get("genre_list", []),
        "cast": row.get("cast_str", "N/A"),
        "popularity": float(row.get("popularity", 0.0)),
        "poster": poster_url,
        "default_poster": str(DEFAULT_POSTER_PATH) if DEFAULT_POSTER_PATH.exists() else None
    }


# ==========================================================
# RECOMMENDATION ALGORITHMS
# ==========================================================

def recommend(
    movie_name: str,
    top_n: int = 10,
    genre_filter: str = "All",
    min_rating: float = 0.0,
    min_year: int = 1900,
    max_year: int = 2030
) -> Tuple[Optional[Dict[str, Any]], Optional[pd.DataFrame]]:
    """
    Computes TF-IDF cosine similarity recommendations with optional hybrid filters:
    - genre_filter: e.g. 'Action', 'Comedy', or 'All'
    - min_rating: minimum IMDB/TMDB rating threshold
    - min_year / max_year: release year filter
    """
    target_clean = movie_name.strip().lower()

    # Find movie index in `movies` dataframe
    movie_match = movies[movies["title"].str.strip().str.lower() == target_clean]
    if movie_match.empty:
        movie_match = movies[movies["title"].str.strip().str.lower().str.startswith(target_clean)]
    if movie_match.empty:
        movie_match = movies[movies["title"].str.strip().str.lower().str.contains(target_clean, regex=False, na=False)]

    if movie_match.empty:
        return None, None

    movie_idx = movie_match.index[0]
    matched_title = movies.iloc[movie_idx]["title"]
    searched_movie = get_movie_details(matched_title)

    # Calculate similarity vector
    similarity_vector = cosine_similarity(
        tfidf_matrix[movie_idx],
        tfidf_matrix
    ).flatten()

    # Sort descending (excluding the target movie itself)
    sorted_indices = np.argsort(similarity_vector)[::-1]
    sorted_indices = [idx for idx in sorted_indices if idx != movie_idx]

    # Map candidate indices to metadata for filtering
    candidate_movies = movies.iloc[sorted_indices].copy()
    candidate_movies["similarity"] = similarity_vector[sorted_indices]

    # Merge with metadata for rich filtering
    merged = candidate_movies.merge(
        metadata[["title_clean", "vote_average", "release_year", "genre_list", "genre_str", "poster_path"]],
        left_on=candidate_movies["title"].str.strip().str.lower(),
        right_on="title_clean",
        how="inner"
    )

    # Apply filters
    if genre_filter != "All":
        merged = merged[merged["genre_list"].apply(lambda g: genre_filter in g)]

    if min_rating > 0.0:
        merged = merged[merged["vote_average"] >= min_rating]

    if min_year > 1900 or max_year < 2030:
        merged = merged[(merged["release_year"] >= min_year) & (merged["release_year"] <= max_year)]

    recommended_df = merged.head(top_n).copy()
    return searched_movie, recommended_df


# ==========================================================
# DISCOVERY MODES (TRENDING, TOP RATED, SURPRISE PICK)
# ==========================================================

def get_trending_movies(limit: int = 8) -> List[Dict[str, Any]]:
    """Returns top popular movies from dataset."""
    top_pop = metadata[metadata["vote_count"] >= 50].sort_values(by="popularity", ascending=False).head(limit)
    res = []
    for _, row in top_pop.iterrows():
        det = get_movie_details(row["title"])
        if det:
            res.append(det)
    return res


def get_top_rated_movies(limit: int = 8, min_votes: int = 300) -> List[Dict[str, Any]]:
    """Returns all-time highest rated classic movies."""
    top_rated = metadata[metadata["vote_count"] >= min_votes].sort_values(by="vote_average", ascending=False).head(limit)
    res = []
    for _, row in top_rated.iterrows():
        det = get_movie_details(row["title"])
        if det:
            res.append(det)
    return res


def get_surprise_movie() -> Optional[Dict[str, Any]]:
    """Returns a random highly rated movie for the user."""
    candidates = metadata[(metadata["vote_average"] >= 7.5) & (metadata["vote_count"] >= 100)]
    if candidates.empty:
        candidates = metadata.head(100)
    random_row = candidates.sample(1).iloc[0]
    return get_movie_details(random_row["title"])


def total_movies_count() -> int:
    """Returns total movies in metadata."""
    return len(metadata)


def total_recommendation_models_count() -> int:
    """Returns total movies in TF-IDF matrix."""
    return len(movies)