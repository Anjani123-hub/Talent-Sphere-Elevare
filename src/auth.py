"""
src/auth.py

Authentication & User Management
Supports:
- Admin/User roles
- Secure password hashing
- SQLite database
"""

import sqlite3
import re
from pathlib import Path

import bcrypt

DB_PATH = Path(__file__).resolve().parent.parent / "talent_sphere_users.db"


# ==========================================================
# DATABASE
# ==========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    create_default_admin()


# ==========================================================
# DEFAULT ADMIN
# ==========================================================

def create_default_admin():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE username=?",
        ("admin",)
    )

    admin = cur.fetchone()

    if admin is None:

        password_hash = bcrypt.hashpw(
            "admin123".encode(),
            bcrypt.gensalt()
        ).decode()

        cur.execute(
            """
            INSERT INTO users
            (
                full_name,
                gender,
                email,
                username,
                password_hash,
                role
            )
            VALUES
            (
                ?,?,?,?,?,?
            )
            """,
            (
                "Administrator",
                "Prefer not to say",
                "admin@talentsphere.ai",
                "admin",
                password_hash,
                "admin",
            ),
        )

        conn.commit()

    conn.close()


# ==========================================================
# VALIDATION
# ==========================================================

def valid_email(email):

    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'

    return re.match(pattern, email) is not None


def hash_password(password):

    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def check_password(password, hashed):

    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )


# ==========================================================
# CREATE USER
# ==========================================================

def create_user(
    full_name,
    gender,
    email,
    username,
    password,
):

    full_name = full_name.strip()

    email = email.strip().lower()

    username = username.strip().lower()

    if (
        not full_name
        or not gender
        or not email
        or not username
        or not password
    ):
        return False, "Please fill all fields."

    if not valid_email(email):
        return False, "Invalid email."

    if len(password) < 6:
        return False, "Password should contain at least 6 characters."

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM users
        WHERE email=?
        OR username=?
        """,
        (
            email,
            username,
        ),
    )

    if cur.fetchone():

        conn.close()

        return (
            False,
            "Email or Username already exists."
        )

    password_hash = hash_password(password)

    cur.execute(
        """
        INSERT INTO users
        (
            full_name,
            gender,
            email,
            username,
            password_hash,
            role
        )
        VALUES
        (
            ?,?,?,?,?,?
        )
        """,
        (
            full_name,
            gender,
            email,
            username,
            password_hash,
            "user",
        ),
    )

    conn.commit()
    conn.close()

    return (
        True,
        "Account Created Successfully."
    )
# ==========================================================
# VERIFY USER LOGIN
# ==========================================================

def verify_user(username_or_email, password):

    identifier = username_or_email.strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            full_name,
            gender,
            email,
            username,
            password_hash,
            role
        FROM users
        WHERE username=?
        OR email=?
        """,
        (
            identifier,
            identifier,
        ),
    )

    row = cur.fetchone()

    conn.close()

    if row is None:
        return None

    if not check_password(password, row["password_hash"]):
        return None

    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "gender": row["gender"],
        "email": row["email"],
        "username": row["username"],
        "role": row["role"],
    }


# ==========================================================
# USER MANAGEMENT
# ==========================================================

def get_all_users():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            full_name,
            gender,
            email,
            username,
            role,
            created_at
        FROM users
        ORDER BY created_at DESC
        """
    )

    users = [dict(row) for row in cur.fetchall()]

    conn.close()

    return users


def delete_user(user_id):

    conn = get_connection()
    cur = conn.cursor()

    # Don't allow deleting the default admin
    cur.execute(
        """
        SELECT username
        FROM users
        WHERE id=?
        """,
        (user_id,),
    )

    row = cur.fetchone()

    if row and row["username"] == "admin":
        conn.close()
        return False

    cur.execute(
        """
        DELETE FROM users
        WHERE id=?
        """,
        (user_id,),
    )

    conn.commit()
    conn.close()

    return True


def update_user_role(user_id, role):

    if role not in ("admin", "user"):
        return False

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET role=?
        WHERE id=?
        """,
        (
            role,
            user_id,
        ),
    )

    conn.commit()
    conn.close()

    return True


def get_user_count():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM users
        """
    )

    count = cur.fetchone()[0]

    conn.close()

    return count


# ==========================================================
# ROLE HELPERS
# ==========================================================

def is_admin(user):

    if not user:
        return False

    return user.get("role") == "admin"


def is_user(user):

    if not user:
        return False

    return user.get("role") == "user"