from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Iterator

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "instance" / "db.sqlite"
SCHEMA_PATH = BASE_DIR / "schema.sql"

sqlite3.register_converter("timestamp", lambda value: datetime.fromisoformat(value.decode()))


def get_database_path() -> Path:
    """Return the SQLite database path used by the FastAPI migration."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection without relying on Flask's request context."""
    conn = sqlite3.connect(
        get_database_path(),
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Context manager for plain database access in FastAPI code."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize SQLite schema using a plain, framework-independent function."""
    with db_session() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def get_db_dependency() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI-style dependency that yields a database connection.

    Example usage:
        def some_route(db: sqlite3.Connection = Depends(get_db_dependency)):
            ...
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
