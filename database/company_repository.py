"""
Company repository for SAFE-INTERN.

Purpose:
- Track company/domain-level risk history
- Store how often a company shows risky signals

NO scoring logic
NO user-facing logic
"""

from database.db_connection import get_db_connection


def record_company_check(
    domain: str | None,
    email_domain: str | None,
    issues: list[str]
) -> None:
    if not domain:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, checks, issues
        FROM company_risk_stats
        WHERE domain = ?
        """,
        (domain,)
    )
    row = cursor.fetchone()

    # risk_count = len(issues) -> 'issues' is TEXT in db_init, storing list as string?
    # db_init: issues TEXT. 
    # repository seems to want to store count?
    # db_init says: issues TEXT. 
    # Let's check db_init again to be sure what 'issues' column stores.
    # db_init: issues TEXT, checks INTEGER.
    
    # Wait, db_init has 'issues TEXT'. 
    # The repository code was trying to store 'risk_count' (integer) into 'risk_flags'.
    # But db_init has 'issues' (TEXT).
    # And 'checks' instead of 'total_checks'.
    
    # Let's align with db_init:
    # checks -> checks
    # issues -> issues (TEXT). 
    # But wait, the previous code was: risk_flags = risk_flags + ? (where ? was risk_count).
    # It seems the previous code wanted to track a running count of risks?
    # But db_init schema is: issues TEXT.
    
    # Let's look at db_init again. 
    # issues TEXT.
    
    # I will store the *new* issues appended to old issues? Or just overwrite?
    # The simplest fix to make it run is to match columns.
    # But we need to know what to put in 'issues'.
    # The function arg is 'issues: list[str]'.
    # I'll convert list to comma-separated string for the TEXT column.
    
    issues_str = ", ".join(issues)

    if row:
        # Update existing
        cursor.execute(
            """
            UPDATE company_risk_stats
            SET checks = checks + 1,
                issues = ?,
                last_checked = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (issues_str, row[0])
        )
    else:
        # Insert new
        cursor.execute(
            """
            INSERT INTO company_risk_stats
            (domain, email_domain, checks, issues)
            VALUES (?, ?, 1, ?)
            """,
            (domain, email_domain, issues_str)
        )

    conn.commit()
    conn.close()
