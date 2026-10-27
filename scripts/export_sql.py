import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser(
        description="Export a SQLite database to a SQL dump."
    )
    parser.add_argument(
        "--database",
        default=str(ROOT / "data" / "employee_performance.db"),
        help="SQLite database to export"
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "generated" / "employee_performance_seed.sql"),
        help="Destination SQL file"
    )
    args = parser.parse_args()

    db_path = Path(args.database).resolve()
    out_path = Path(args.output).resolve()

    if not db_path.is_file():
        raise SystemExit(f"Database not found: {db_path}")
    if db_path == out_path:
        raise SystemExit("Output must not overwrite the database.")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(db_path)) as connection:
        with out_path.open("w", encoding="utf-8", newline="\n") as output:
            for line in connection.iterdump():
                output.write(line + "\n")

    print("SQL export created:", out_path)
    print("Source database:", db_path)
    print("File size:", out_path.stat().st_size, "bytes")

if __name__ == "__main__":
    main()
