import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parent.parent
db_path = root / "data" / "employee_performance.db"
out_path = root / "data" / "generated" / "employee_performance_seed.sql"

if not db_path.exists():
    raise SystemExit(f"Database not found: {db_path}")

out_path.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(db_path) as connection:
    with out_path.open("w", encoding="utf-8", newline="\n") as output:
        for line in connection.iterdump():
            output.write(line + "\n")

print("SQL export created:", out_path)
print("File size:", out_path.stat().st_size, "bytes")
