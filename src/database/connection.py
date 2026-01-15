"""Database connection management."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


_connection: sqlite3.Connection | None = None


def init_database(db_path: Path) -> None:
    """Initialize the database, creating tables if needed."""
    global _connection
    
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _connection = sqlite3.connect(db_path, check_same_thread=False)
    _connection.row_factory = sqlite3.Row
    _connection.execute("PRAGMA foreign_keys = ON")
    
    from src.database.migrations.runner import run_migrations
    run_migrations(_connection)


def get_connection() -> sqlite3.Connection:
    """Get the database connection."""
    if _connection is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _connection


@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database transactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise