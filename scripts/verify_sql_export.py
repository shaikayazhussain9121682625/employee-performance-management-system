import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sql_path = root / "data" / "generated" / "employee_performance_seed.sql"

if not sql_path.exists():
    raise SystemExit(f"SQL export not found: {sql_path}")

connection = sqlite3.connect(":memory:")

try:
    # Allow tables and rows to be restored in dependency order.
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.executescript(sql_path.read_text(encoding="utf-8-sig"))

    # Re-enable foreign-key enforcement and check existing records.
    connection.execute("PRAGMA foreign_keys = ON")

    tables = [
        row[0]
        for row in connection.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
    ]

    print("SQL export restored successfully.")
    print("Tables:", len(tables))

    for table in tables:
        count = connection.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        ).fetchone()[0]
        print(f"{table}: {count:,} rows")

    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    print("Foreign-key violations:", len(violations))

    if violations:
        for violation in violations[:20]:
            print(violation)
        raise SystemExit("FAIL: foreign-key violations found.")

    print("RESULT: PASS")

finally:
    connection.close()
