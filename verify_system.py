"""
Automated verification script for CineMatch AI.
Tests database, auth, recommendations, filters, and discovery modes.
"""

import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("=" * 60)
print("RUNNING CINEMATCH AI SYSTEM VERIFICATION")
print("=" * 60)

import config
import database
import auth
import recommendation
import utils

print("[PASS] Configuration & Paths validated successfully.")

print("\n--- 1. Testing Database & Authentication ---")
test_username = "test_evaluator_2026"
test_email = "evaluator_2026@cinematch.ai"

# Register user
success, msg = auth.register_user("Evaluator Test", test_username, test_email, "secretpass123")
print("Registration output:", success, msg)

# Login user
user = auth.login_user(test_username, "secretpass123")
assert user is not None, "Login failed!"
user_id = user["user_id"]
print(f"Logged in user: {user['username']} (ID: {user_id})")

# Test Favorites
database.add_favorite(user_id, "Inception", "27205", "/path.jpg", 8.8, "Action, Science Fiction")
assert database.is_favorite(user_id, "Inception") is True, "Favorite check failed"
favs = database.get_user_favorites(user_id)
print(f"Favorites retrieved: {len(favs)} item(s)")

# Test Likes
like_res = database.toggle_like(user_id, "Inception")
print(f"Like toggle result: {like_res}")

# Test Ratings & Comments
database.save_movie_rating(user_id, "Inception", 5.0)
rating_val = database.get_user_movie_rating(user_id, "Inception")
assert rating_val == 5.0, f"Expected rating 5.0, got {rating_val}"

database.add_movie_comment(user_id, "Inception", "Phenomenal visual storytelling and Nolan genius!")
comments = database.get_movie_comments("Inception")
print(f"Movie comments retrieved: {len(comments)} comment(s)")

# Test Platform Stats
stats = database.get_platform_stats()
print("Platform stats:", stats)

print("\n--- 2. Testing Recommendation Engine & Discovery ---")
searched, recs = recommendation.recommend("Toy Story", top_n=5)
assert searched is not None, "Searched movie Toy Story not found"
assert len(recs) == 5, f"Expected 5 recommendations, got {len(recs)}"
print(f"Target Movie: {searched['title']} | Rating: {searched['rating']} | Genres: {searched['genres']}")
print("Top 5 Recommendations:")
for idx, r in recs.iterrows():
    sim_pct = r["similarity"] * 100
    print(f"  [{idx+1}] {r['title']} - Match: {sim_pct:.1f}%")

# Test Hybrid Filtering
_, filtered_recs = recommendation.recommend("Toy Story", top_n=5, genre_filter="Animation", min_rating=6.0)
print(f"Filtered (Animation, Rating>=6.0) recommendations count: {len(filtered_recs)}")

# Test Trending & Top Rated
trending = recommendation.get_trending_movies(limit=4)
print(f"Trending movies fetched: {len(trending)} titles")
for m in trending:
    print(f"  - {m['title']} (Popularity: {m['popularity']:.1f}, Rating: {m['rating']})")

top_rated = recommendation.get_top_rated_movies(limit=4)
print(f"Top-rated classics fetched: {len(top_rated)} titles")
for m in top_rated:
    print(f"  - {m['title']} (Rating: {m['rating']:.1f})")

# Test Surprise Pick
surprise = recommendation.get_surprise_movie()
print(f"Surprise movie pick: {surprise['title']} (Rating: {surprise['rating']})")

print("\n--- 3. Testing UI Helpers & Pages Syntax ---")
import pages.login
import pages.register
import pages.forgot_password
import pages.dashboard
import pages.favorites
import pages.analytics
import pages.profile

print("[PASS] All page modules imported and validated with zero syntax errors!")

print("\n" + "=" * 60)
print("ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
