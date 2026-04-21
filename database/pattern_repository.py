"""
Generic pattern tracking for SAFE-INTERN.

Used by:
- payment_agent
- behavior_agent
- ml_agent

NO scoring logic
"""

from database.db_connection import get_db_connection


def record_pattern(pattern_type: str, pattern_key: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM risk_patterns
        WHERE pattern_type = ? AND pattern_key = ?
        """,
        (pattern_type, pattern_key)
    )

    row = cursor.fetchone()

    if row:
        cursor.execute(
            """
            UPDATE risk_patterns
            SET occurrences = occurrences + 1,
                last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (row[0],)
        )
    else:
        cursor.execute(
            """
            INSERT INTO risk_patterns (pattern_type, pattern_key, occurrences)
            VALUES (?, ?, 1)
            """,
            (pattern_type, pattern_key)
        )

    conn.commit()
    conn.close()
