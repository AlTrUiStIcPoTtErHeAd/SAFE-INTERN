import sqlite3
from config.settings import DATABASE_PATH


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # -------------------------------
    # COMPANY RISK STATS TABLE
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_risk_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE,
            email_domain TEXT,
            issues TEXT,
            checks INTEGER DEFAULT 1,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------------
    # RISK PATTERNS TABLE
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            pattern_key TEXT,
            occurrences INTEGER DEFAULT 1,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pattern_type, pattern_key)
        )
    """)

    # -------------------------------
    # METADATA TABLE
    # -------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")
