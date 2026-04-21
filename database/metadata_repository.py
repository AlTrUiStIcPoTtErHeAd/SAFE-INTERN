# database/metadata_repository.py
"""
Metadata repository for SAFE-INTERN.

Responsibilities:
- Store system-level metadata
- Track ML model versions and timestamps
- Track schema / pipeline versions
- Store last update info for reproducibility

Used for:
- Debugging
- Auditing
- Model & system transparency

NO user data
NO risk scoring
NO decision logic
"""

from typing import Optional, Dict, Any
from database.db_connection import get_db_connection


# ---------- INSERT / UPDATE METADATA ----------

def upsert_metadata(
    key: str,
    value: str,
    description: Optional[str] = None
) -> None:
    """
    Insert or update a metadata key-value pair.

    Args:
        key: Metadata key (e.g., model_version)
        value: Metadata value
        description: Optional human-readable description
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO metadata (
            key,
            value,
            description,
            updated_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key)
        DO UPDATE SET
            value = excluded.value,
            description = excluded.description,
            updated_at = CURRENT_TIMESTAMP
        """,
        (key, value, description)
    )

    conn.commit()
    conn.close()


# ---------- QUERY HELPERS ----------

def get_metadata(key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata by key.

    Args:
        key: Metadata key

    Returns:
        Dictionary with metadata fields or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT key, value, description, updated_at
        FROM metadata
        WHERE key = ?
        """,
        (key,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "key": row[0],
        "value": row[1],
        "description": row[2],
        "updated_at": row[3]
    }


def get_all_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all metadata entries.

    Returns:
        Dictionary keyed by metadata key
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT key, value, description, updated_at
        FROM metadata
        ORDER BY key
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return {
        row[0]: {
            "value": row[1],
            "description": row[2],
            "updated_at": row[3]
        }
        for row in rows
    }
