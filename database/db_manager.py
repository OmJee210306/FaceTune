import sqlite3
import logging
import os
from datetime import datetime
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    song_path TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)
        logger.info("Database initialized at %s", self.db_path)

    def add_user(self, name: str, song_path: Optional[str] = None) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO users (name, song_path, created_at) VALUES (?, ?, ?)",
                    (name, song_path, datetime.now().isoformat())
                )
            logger.info("User added: %s", name)
            return True
        except sqlite3.IntegrityError:
            logger.warning("User already exists: %s", name)
            return False
        except Exception as e:
            logger.error("Error adding user %s: %s", name, e)
            return False

    def delete_user(self, name: str) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute("DELETE FROM users WHERE name = ?", (name,))
            logger.info("User deleted: %s", name)
            return True
        except Exception as e:
            logger.error("Error deleting user %s: %s", name, e)
            return False

    def update_user_song(self, name: str, song_path: str) -> bool:
        try:
            with self._get_conn() as conn:
                conn.execute(
                    "UPDATE users SET song_path = ? WHERE name = ?",
                    (song_path, name)
                )
            logger.info("Song updated for user %s: %s", name, song_path)
            return True
        except Exception as e:
            logger.error("Error updating song for %s: %s", name, e)
            return False

    def get_user(self, name: str) -> Optional[dict]:
        try:
            with self._get_conn() as conn:
                row = conn.execute(
                    "SELECT * FROM users WHERE name = ?", (name,)
                ).fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error("Error fetching user %s: %s", name, e)
            return None

    def get_all_users(self) -> List[dict]:
        try:
            with self._get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM users ORDER BY created_at DESC"
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error("Error fetching all users: %s", e)
            return []

    def user_exists(self, name: str) -> bool:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE name = ?", (name,)
            ).fetchone()
            return row is not None

    def add_log(self, user_name: str, status: str):
        try:
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO logs (user_name, status, timestamp) VALUES (?, ?, ?)",
                    (user_name, status, datetime.now().isoformat())
                )
        except Exception as e:
            logger.error("Error adding log: %s", e)

    def get_logs(self, limit: int = 200) -> List[dict]:
        try:
            with self._get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,)
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error("Error fetching logs: %s", e)
            return []

    def clear_logs(self):
        try:
            with self._get_conn() as conn:
                conn.execute("DELETE FROM logs")
            logger.info("Logs cleared")
        except Exception as e:
            logger.error("Error clearing logs: %s", e)
