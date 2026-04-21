# database/db_connection.py
"""
Database connection handler for SAFE-INTERN.

Responsibilities:
- Create and manage SQLite database connections
- Ensure foreign key support
- Provide a single, reusable connection interface

NO business logic
NO queries
"""

import sqlite3
from pathlib import Path
from typing import Optional

# Database file path
DB_PATH = Path(__file__).parent / "safe_intern.db"


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.

    Args:
        db_path: Optional custom database path (defaults to safe_intern.db)

    Returns:
        sqlite3.Connection object
    """
    path = db_path if db_path else DB_PATH

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # Access columns by name

    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn
