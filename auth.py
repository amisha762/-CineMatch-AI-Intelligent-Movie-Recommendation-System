"""
Authentication module for Movie Recommendation System.
Handles registration, login, password resets, profile management, and password hashing.
"""

import re
import sqlite3
import bcrypt
from typing import Tuple, Optional, Dict, Any
from database import get_db_connection


def validate_email(email: str) -> bool:
    """Validates email format using regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def register_user(full_name: str, username: str, email: str, password: str) -> Tuple[bool, str]:
    """Registers a new user with secure password hashing."""
    full_name = full_name.strip()
    username = username.strip().lower()
    email = email.strip().lower()
    password = password.strip()

    if not full_name or not username or not email or not password:
        return False, "All fields are required."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            # Check for existing username
            cursor.execute("SELECT user_id FROM users WHERE LOWER(username) = ?", (username,))
            if cursor.fetchone():
                return False, "Username is already taken."

            # Check for existing email
            cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = ?", (email,))
            if cursor.fetchone():
                return False, "Email is already registered."

            # Hash password
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            cursor.execute(
                """
                INSERT INTO users (full_name, username, email, password)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, username, email, hashed_pw)
            )
            conn.commit()
            return True, "Account created successfully! You can now log in."

        except Exception as e:
            return False, f"Registration failed: {str(e)}"


def login_user(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates a user by username or email and returns user record if valid."""
    identifier = username_or_email.strip().lower()
    password = password.strip()

    if not identifier or not password:
        return None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id, full_name, username, email, password, is_admin, avatar_url, created_at
            FROM users
            WHERE LOWER(username) = ? OR LOWER(email) = ?
            """,
            (identifier, identifier)
        )
        user = cursor.fetchone()

        if user:
            stored_pw = user["password"]
            if isinstance(stored_pw, str):
                stored_pw = stored_pw.encode("utf-8")

            if bcrypt.checkpw(password.encode("utf-8"), stored_pw):
                return dict(user)

    return None


def reset_password(email: str, new_password: str) -> Tuple[bool, str]:
    """Resets user password given a registered email."""
    email = email.strip().lower()
    new_password = new_password.strip()

    if not email or not new_password:
        return False, "Email and new password are required."

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters long."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return False, "No account found with this email address."

        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute("UPDATE users SET password = ? WHERE LOWER(email) = ?", (hashed_pw, email))
        conn.commit()
        return True, "Password has been successfully updated! You can now log in."


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Fetches user details by username."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, full_name, username, email, is_admin, avatar_url, created_at FROM users WHERE LOWER(username) = ?",
            (username.strip().lower(),)
        )
        user = cursor.fetchone()
        return dict(user) if user else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetches user details by user_id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, full_name, username, email, is_admin, avatar_url, created_at FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        return dict(user) if user else None


def update_user_profile(user_id: int, full_name: str, email: str) -> Tuple[bool, str]:
    """Updates user profile information."""
    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name or not email:
        return False, "Full name and email cannot be empty."

    if not validate_email(email):
        return False, "Please provide a valid email."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Check email uniqueness for other users
        cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = ? AND user_id != ?", (email, user_id))
        if cursor.fetchone():
            return False, "This email is already in use by another account."

        cursor.execute(
            "UPDATE users SET full_name = ?, email = ? WHERE user_id = ?",
            (full_name, email, user_id)
        )
        conn.commit()
        return True, "Profile updated successfully."


def change_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
    """Changes password for an authenticated user."""
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False, "User not found."

        stored_pw = row["password"]
        if isinstance(stored_pw, str):
            stored_pw = stored_pw.encode("utf-8")

        if not bcrypt.checkpw(current_password.encode("utf-8"), stored_pw):
            return False, "Incorrect current password."

        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (hashed_pw, user_id))
        conn.commit()
        return True, "Password changed successfully."