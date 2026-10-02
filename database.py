"""
Database module for Movie Recommendation System.
Handles SQLite operations, connection pooling, schema migrations, and CRUD operations.
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from config import DATABASE_PATH


@contextmanager
def get_db_connection():
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def get_connection():
    """Returns a direct connection for compatibility."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Initializes the database and ensures all required tables and columns exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            avatar_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Search History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_title TEXT NOT NULL,
            search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        # Favorites Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_title TEXT NOT NULL,
            movie_id TEXT DEFAULT '',
            poster_path TEXT DEFAULT '',
            rating REAL DEFAULT 0,
            genre TEXT DEFAULT '',
            added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        # Likes Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            like_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_title TEXT NOT NULL,
            liked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        # Dislikes Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dislikes (
            dislike_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_title TEXT NOT NULL,
            disliked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        # Ratings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_title TEXT NOT NULL,
            rating REAL CHECK(rating >= 1 AND rating <= 5),
            rating_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        # Comments / Reviews Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_title TEXT NOT NULL,
            comment TEXT NOT NULL,
            comment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)

        # Schema Migrations for existing tables (using constant defaults)
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [r[1] for r in cursor.fetchall()]
        if "avatar_url" not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT ''")

        cursor.execute("PRAGMA table_info(favorites)")
        fav_cols = [r[1] for r in cursor.fetchall()]
        if "movie_id" not in fav_cols:
            cursor.execute("ALTER TABLE favorites ADD COLUMN movie_id TEXT DEFAULT ''")
        if "poster_path" not in fav_cols:
            cursor.execute("ALTER TABLE favorites ADD COLUMN poster_path TEXT DEFAULT ''")
        if "rating" not in fav_cols:
            cursor.execute("ALTER TABLE favorites ADD COLUMN rating REAL DEFAULT 0")
        if "genre" not in fav_cols:
            cursor.execute("ALTER TABLE favorites ADD COLUMN genre TEXT DEFAULT ''")

        cursor.execute("PRAGMA table_info(dislikes)")
        dislike_cols = [r[1] for r in cursor.fetchall()]
        if "disliked_time" not in dislike_cols:
            cursor.execute("ALTER TABLE dislikes ADD COLUMN disliked_time TIMESTAMP DEFAULT NULL")

        conn.commit()


# Auto-initialize database on import
init_database()


# ==========================================================
# SEARCH HISTORY
# ==========================================================

def save_search(user_id: int, movie_title: str) -> None:
    """Saves user search to history."""
    if not user_id or not movie_title:
        return
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO search_history (user_id, movie_title)
            VALUES (?, ?)
            """,
            (user_id, movie_title.strip())
        )
        conn.commit()


def get_user_search_history(user_id: int, limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves recent search history for a user."""
    if not user_id:
        return []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT movie_title, search_time
            FROM search_history
            WHERE user_id = ?
            ORDER BY search_time DESC
            LIMIT ?
            """,
            (user_id, limit)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def clear_user_search_history(user_id: int) -> bool:
    """Clears all search history for a user."""
    if not user_id:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
        conn.commit()
        return True


def get_popular_searches(limit: int = 6) -> List[Dict[str, Any]]:
    """Returns the most frequently searched movie titles across all users."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT movie_title, COUNT(*) as count
            FROM search_history
            GROUP BY movie_title
            ORDER BY count DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


# ==========================================================
# FAVORITES MANAGEMENT
# ==========================================================

def add_favorite(user_id: int, movie_title: str, movie_id: str = "", poster_path: str = "", rating: float = 0.0, genre: str = "") -> bool:
    """Adds a movie to the user's favorites if not already present."""
    if not user_id or not movie_title:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT favorite_id FROM favorites WHERE user_id=? AND movie_title=?",
            (user_id, movie_title.strip())
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO favorites (user_id, movie_title, movie_id, poster_path, rating, genre)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, movie_title.strip(), str(movie_id), str(poster_path), float(rating), str(genre))
            )
            conn.commit()
            return True
        return False


def remove_favorite(user_id: int, movie_title: str) -> bool:
    """Removes a movie from the user's favorites."""
    if not user_id or not movie_title:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM favorites WHERE user_id=? AND movie_title=?",
            (user_id, movie_title.strip())
        )
        conn.commit()
        return cursor.rowcount > 0


def is_favorite(user_id: int, movie_title: str) -> bool:
    """Checks if a movie is in user's favorites."""
    if not user_id or not movie_title:
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT favorite_id FROM favorites WHERE user_id=? AND movie_title=?",
            (user_id, movie_title.strip())
        )
        return cursor.fetchone() is not None


def get_user_favorites(user_id: int) -> List[Dict[str, Any]]:
    """Retrieves all favorited movies for a user."""
    if not user_id:
        return []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT favorite_id, movie_title, movie_id, poster_path, rating, genre, added_time
            FROM favorites
            WHERE user_id = ?
            ORDER BY added_time DESC
            """,
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def count_user_favorites(user_id: int) -> int:
    """Counts user's total favorites."""
    if not user_id:
        return 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = ?", (user_id,))
        res = cursor.fetchone()
        return res[0] if res else 0


# ==========================================================
# LIKES & DISLIKES MANAGEMENT
# ==========================================================

def toggle_like(user_id: int, movie_title: str) -> str:
    """Toggles like on a movie. If disliked, removes dislike."""
    if not user_id or not movie_title:
        return "error"
    title = movie_title.strip()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Remove any existing dislike
        cursor.execute("DELETE FROM dislikes WHERE user_id=? AND movie_title=?", (user_id, title))
        
        # Check if already liked
        cursor.execute("SELECT like_id FROM likes WHERE user_id=? AND movie_title=?", (user_id, title))
        if cursor.fetchone():
            cursor.execute("DELETE FROM likes WHERE user_id=? AND movie_title=?", (user_id, title))
            conn.commit()
            return "unliked"
        else:
            cursor.execute("INSERT INTO likes (user_id, movie_title) VALUES (?, ?)", (user_id, title))
            conn.commit()
            return "liked"


def toggle_dislike(user_id: int, movie_title: str) -> str:
    """Toggles dislike on a movie. If liked, removes like."""
    if not user_id or not movie_title:
        return "error"
    title = movie_title.strip()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Remove any existing like
        cursor.execute("DELETE FROM likes WHERE user_id=? AND movie_title=?", (user_id, title))
        
        # Check if already disliked
        cursor.execute("SELECT dislike_id FROM dislikes WHERE user_id=? AND movie_title=?", (user_id, title))
        if cursor.fetchone():
            cursor.execute("DELETE FROM dislikes WHERE user_id=? AND movie_title=?", (user_id, title))
            conn.commit()
            return "undisliked"
        else:
            cursor.execute("INSERT INTO dislikes (user_id, movie_title) VALUES (?, ?)", (user_id, title))
            conn.commit()
            return "disliked"


def get_movie_user_reaction(user_id: int, movie_title: str) -> Optional[str]:
    """Returns 'liked', 'disliked', or None for user's reaction to a movie."""
    if not user_id or not movie_title:
        return None
    title = movie_title.strip()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT like_id FROM likes WHERE user_id=? AND movie_title=?", (user_id, title))
        if cursor.fetchone():
            return "liked"
        cursor.execute("SELECT dislike_id FROM dislikes WHERE user_id=? AND movie_title=?", (user_id, title))
        if cursor.fetchone():
            return "disliked"
    return None


def get_movie_reaction_counts(movie_title: str) -> Dict[str, int]:
    """Returns total likes and dislikes for a given movie."""
    title = movie_title.strip()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM likes WHERE movie_title=?", (title,))
        likes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM dislikes WHERE movie_title=?", (title,))
        dislikes = cursor.fetchone()[0]
        return {"likes": likes, "dislikes": dislikes}


# ==========================================================
# RATINGS & REVIEWS
# ==========================================================

def save_movie_rating(user_id: int, movie_title: str, rating: float) -> bool:
    """Inserts or updates a user rating for a movie."""
    if not user_id or not movie_title:
        return False
    title = movie_title.strip()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rating_id FROM ratings WHERE user_id=? AND movie_title=?", (user_id, title))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE ratings SET rating=?, rating_time=CURRENT_TIMESTAMP WHERE user_id=? AND movie_title=?",
                (rating, user_id, title)
            )
        else:
            cursor.execute(
                "INSERT INTO ratings (user_id, movie_title, rating) VALUES (?, ?, ?)",
                (user_id, title, rating)
            )
        conn.commit()
        return True


def get_user_movie_rating(user_id: int, movie_title: str) -> Optional[float]:
    """Returns the rating given by a user to a specific movie."""
    if not user_id or not movie_title:
        return None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rating FROM ratings WHERE user_id=? AND movie_title=?",
            (user_id, movie_title.strip())
        )
        row = cursor.fetchone()
        return row[0] if row else None


def get_movie_community_rating(movie_title: str) -> Dict[str, Any]:
    """Returns average community rating and total rating votes."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT AVG(rating), COUNT(rating) FROM ratings WHERE movie_title=?",
            (movie_title.strip(),)
        )
        row = cursor.fetchone()
        avg = round(row[0], 1) if row and row[0] is not None else 0.0
        count = row[1] if row else 0
        return {"avg_rating": avg, "total_ratings": count}


def add_movie_comment(user_id: int, movie_title: str, comment: str) -> bool:
    """Adds a user comment/review for a movie."""
    if not user_id or not movie_title or not comment.strip():
        return False
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comments (user_id, movie_title, comment) VALUES (?, ?, ?)",
            (user_id, movie_title.strip(), comment.strip())
        )
        conn.commit()
        return True


def get_movie_comments(movie_title: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves comments for a specific movie with username information."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.comment_id, c.comment, c.comment_time, u.username, u.full_name
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.movie_title = ?
            ORDER BY c.comment_time DESC
            LIMIT ?
            """,
            (movie_title.strip(), limit)
        )
        return [dict(row) for row in cursor.fetchall()]


# ==========================================================
# PLATFORM & USER ANALYTICS
# ==========================================================

def get_platform_stats() -> Dict[str, int]:
    """Returns aggregate statistics for the entire application."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM favorites")
        total_favorites = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM likes")
        total_likes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM search_history")
        total_searches = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ratings")
        total_ratings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM comments")
        total_comments = cursor.fetchone()[0]
        
        return {
            "users": total_users,
            "favorites": total_favorites,
            "likes": total_likes,
            "searches": total_searches,
            "ratings": total_ratings,
            "comments": total_comments
        }


def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Returns activity statistics for a specific user."""
    if not user_id:
        return {"favorites": 0, "likes": 0, "dislikes": 0, "searches": 0, "ratings": 0, "comments": 0}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id=?", (user_id,))
        favs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM likes WHERE user_id=?", (user_id,))
        likes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dislikes WHERE user_id=?", (user_id,))
        dislikes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM search_history WHERE user_id=?", (user_id,))
        searches = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE user_id=?", (user_id,))
        ratings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM comments WHERE user_id=?", (user_id,))
        comments = cursor.fetchone()[0]
        
        return {
            "favorites": favs,
            "likes": likes,
            "dislikes": dislikes,
            "searches": searches,
            "ratings": ratings,
            "comments": comments
        }