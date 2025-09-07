import os
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from .config import settings


def _ensure_parent_dir(db_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)


def init_db() -> None:
    _ensure_parent_dir(settings.db_path)
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                is_admin INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL,
                peer_id TEXT NOT NULL UNIQUE,
                name TEXT,
                username TEXT,
                expires_at INTEGER,
                FOREIGN KEY(tg_id) REFERENCES users(tg_id)
            );
            """
        )
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(settings.db_path)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()


def ensure_user(tg_id: int, is_admin: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (tg_id, is_admin) VALUES (?, ?)",
            (tg_id, 1 if is_admin else 0),
        )
        conn.execute(
            "UPDATE users SET is_admin = ? WHERE tg_id = ?",
            (1 if is_admin else 0, tg_id),
        )
        conn.commit()


def get_client_by_tg(tg_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM clients WHERE tg_id = ? LIMIT 1", (tg_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def upsert_client(tg_id: int, peer_id: str, name: Optional[str], expires_at: Optional[int], username: Optional[str] = None) -> None:
    with get_conn() as conn:
        existing = conn.execute("SELECT id FROM clients WHERE peer_id = ?", (peer_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE clients SET tg_id = ?, name = ?, expires_at = ?, username = ? WHERE peer_id = ?",
                (tg_id, name, expires_at, username, peer_id),
            )
        else:
            conn.execute(
                "INSERT INTO clients (tg_id, peer_id, name, expires_at, username) VALUES (?, ?, ?, ?, ?)",
                (tg_id, peer_id, name, expires_at, username),
            )
        conn.commit()


def set_expiry(peer_id: str, expires_at: Optional[int]) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE clients SET expires_at = ? WHERE peer_id = ?", (expires_at, peer_id))
        conn.commit()


def now_ts() -> int:
    return int(time.time())


def get_all_clients() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM clients ORDER BY name")
        return [dict(row) for row in cur.fetchall()]


def get_client_by_peer_id(peer_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM clients WHERE peer_id = ? LIMIT 1", (peer_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def delete_client(peer_id: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM clients WHERE peer_id = ?", (peer_id,))
        conn.commit()


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Получить пользователя по username (без @)"""
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM users WHERE tg_id IN (SELECT tg_id FROM clients WHERE username = ?)", (username,))
        row = cur.fetchone()
        return dict(row) if row else None
