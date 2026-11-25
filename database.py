import sqlite3
from datetime import datetime, timezone

DB_NAME = "urls.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Lets you access columns by name
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                clicks INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code)")


def save_url(short_code: str, original_url: str):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO urls (short_code, original_url, created_at) VALUES (?, ?, ?)",
            (short_code, original_url, created_at),
        )


def get_url(short_code: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        return dict(row) if row else None


def increment_clicks(short_code: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,)
        )