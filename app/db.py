import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import get_settings


def _connect() -> sqlite3.Connection:
    db_path = Path(get_settings().database_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                is_critic INTEGER NOT NULL CHECK (is_critic IN (0,1))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS movie_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tmdb_movie_id INTEGER NOT NULL,
                rating REAL NOT NULL CHECK (rating >= 0 AND rating <= 10),
                review_text TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, tmdb_movie_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
