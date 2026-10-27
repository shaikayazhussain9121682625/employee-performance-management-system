# Employee Performance Management System — Data Exports

## Contents

- `exports/csv/`: CSV exports for the 12 application tables.
- `exports/json/`: JSON exports for the same 12 application tables.
- `exports/sql/employee_performance_seed.sql`: SQLite SQL dump.
- `exports/export_manifest.json`: Record counts, file sizes, and SHA-256 checksums.

## Dataset

- Random seed: `20261022`
- Total application records: `67,542`
- Application tables: `12`
- Ground-truth anomaly labels: excluded from these exports.

## Reproduction

Run these commands from the repository root:

```powershell
python scripts/generate_data.py --seed 20261022 --employees 3000 --managers 500 --goals 10000 --checkins 20000 --feedback 5000 --output-dir data/generated_v3
python backend/import_data.py --data-dir data/generated_v3 --database data/new_verification.db
```

The example uses a new database filename to avoid overwriting an existing database.

## Validation

The exports were checked for matching JSON and SQL row counts, successful SQL restoration, foreign-key violations, and manifest checksums.

Ground-truth anomaly labels are intentionally excluded from the submission exports.
