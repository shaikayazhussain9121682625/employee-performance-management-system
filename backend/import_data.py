import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path

from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Allow this script to run from the project root with:
# python backend/import_data.py
sys.path.insert(0, str(BACKEND_DIR))

from config import Config  # noqa: E402
from extensions import db  # noqa: E402
import models  # noqa: E402


DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "generated_v3"
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "import_test_v3.db"

# Parent tables must be imported before tables that reference them.
IMPORT_ORDER = [
    ("managers.csv", models.Manager),
    ("employees.csv", models.Employee),
    ("review_cycles.csv", models.ReviewCycle),
    ("competencies.csv", models.Competency),
    ("goals.csv", models.Goal),
    ("key_results.csv", models.KeyResult),
    ("check_ins.csv", models.CheckIn),
    ("reviews.csv", models.Review),
    ("feedback.csv", models.Feedback),
    ("development_plans.csv", models.DevelopmentPlan),
    ("event_history.csv", models.EventHistory),
    ("manager_assignment_history.csv", models.ManagerAssignmentHistory),
]

# Explicit CSV-header-to-model-attribute mappings.
# ground_truth.csv and ground_truth.json are intentionally not imported.
COLUMN_MAP = {
    "managers.csv": {
        "manager_id": "manager_id",
        "full_name": "full_name",
        "email": "email",
        "department": "department",
    },
    "employees.csv": {
        "employee_id": "employee_id",
        "full_name": "full_name",
        "email": "email",
        "department": "department",
        "job_title": "job_title",
        "hire_date": "hire_date",
        "employment_status": "employment_status",
        "manager_id": "manager_id",
    },
    "review_cycles.csv": {
        "cycle_id": "cycle_id",
        "name": "name",
        "start_date": "start_date",
        "end_date": "end_date",
        "status": "status",
    },
    "competencies.csv": {
        "competency_id": "competency_id",
        "name": "name",
        "description": "description",
    },
    "goals.csv": {
        "goal_id": "goal_id",
        "employee_id": "employee_id",
        "cycle_id": "cycle_id",
        "title": "title",
        "status": "status",
        "progress_percent": "progress_percent",
        "created_date": "created_date",
    },
    "key_results.csv": {
        "key_result_id": "key_result_id",
        "goal_id": "goal_id",
        "description": "description",
        "target_value": "target_value",
        "current_value": "current_value",
        "unit": "unit",
    },
    "check_ins.csv": {
        "check_in_id": "check_in_id",
        "employee_id": "employee_id",
        "cycle_id": "cycle_id",
        "check_in_date": "check_in_date",
        "progress_percent": "progress_percent",
        "notes": "notes",
        "rationale": "rationale",
    },
    "reviews.csv": {
        "review_id": "review_id",
        "employee_id": "employee_id",
        "cycle_id": "cycle_id",
        "reviewer_id": "reviewer_id",
        "score": "score",
        "status": "status",
        "review_date": "review_date",
    },
    "feedback.csv": {
        "feedback_id": "feedback_id",
        "employee_id": "employee_id",
        "competency_id": "competency_id",
        "cycle_id": "cycle_id",
        "author_id": "author_id",
        "feedback_type": "feedback_type",
        "evidence_reference": "evidence_reference",
        "rating": "rating",
        "comments": "comments",
        "feedback_date": "feedback_date",
    },
    "development_plans.csv": {
        "development_plan_id": "development_plan_id",
        "employee_id": "employee_id",
        "review_id": "review_id",
        "objective": "objective",
        "action": "action",
        "target_date": "target_date",
        "status": "status",
        "approval_status": "approval_status",
        "approved_by": "approved_by",
        "approved_at": "approved_at",
    },
    "event_history.csv": {
        "event_id": "event_id",
        "cycle_id": "cycle_id",
        "entity_type": "entity_type",
        "record_id": "record_id",
        "event_type": "event_type",
        "actor_id": "actor_id",
        "event_time": "event_time",
        "reason": "reason",
    },
    "manager_assignment_history.csv": {
        "assignment_id": "assignment_id",
        "employee_id": "employee_id",
        "manager_id": "manager_id",
        "effective_from": "effective_from",
        "effective_to": "effective_to",
        "reason": "reason",
        "recorded_at": "recorded_at",
    },
}


def convert_value(value, column):
    """Convert a CSV cell to the Python type expected by a model column."""
    if value is None or value.strip() == "":
        return None

    python_type = column.type.python_type

    if python_type is date:
        return date.fromisoformat(value)
    if python_type is datetime:
        return datetime.fromisoformat(value)
    if python_type is int:
        return int(value)
    if python_type is float:
        return float(value)

    return value


def import_table(data_dir, filename, model):
    """Read one CSV and add its rows to the current SQLAlchemy session."""
    path = data_dir / filename
    mapping = COLUMN_MAP[filename]
    model_columns = {column.name: column for column in model.__table__.columns}
    count = 0

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        missing_headers = set(mapping) - set(headers)

        if missing_headers:
            raise ValueError(
                f"{filename} is missing required columns: "
                f"{sorted(missing_headers)}"
            )

        for row in reader:
            record = {}

            for csv_column, model_column in mapping.items():
                column = model_columns[model_column]
                value = convert_value(row.get(csv_column), column)

                if (
                    value is None
                    and not column.nullable
                    and column.default is None
                    and column.server_default is None
                ):
                    raise ValueError(
                        f"{filename}, CSV line {reader.line_num}: "
                        f"required field '{csv_column}' is empty"
                    )

                record[model_column] = value

            db.session.add(model(**record))
            count += 1

            # Flush in batches to catch constraint errors without waiting
            # until every row in a large file has been queued.
            if count % 1000 == 0:
                db.session.flush()

    db.session.flush()
    print(f"Imported {count:,} rows from {filename}")
    return count


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Import generated employee-performance CSV data into a SQLite "
            "database. The default destination is a separate test database."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Directory containing generated CSV files (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"Destination SQLite database (default: {DEFAULT_DATABASE})",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help=(
            "Allow an existing destination file. Use only when you have "
            "verified it is an empty database."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = args.data_dir.resolve()
    database_path = args.database.resolve()

    if not data_dir.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    missing_files = [
        filename
        for filename, _model in IMPORT_ORDER
        if not (data_dir / filename).is_file()
    ]
    if missing_files:
        raise FileNotFoundError(
            "Missing required input files: " + ", ".join(missing_files)
        )

    database_path.parent.mkdir(parents=True, exist_ok=True)

    if database_path.exists() and not args.allow_existing:
        raise FileExistsError(
            f"Destination database already exists: {database_path}\n"
            "Choose a new --database path, or verify that it is empty before "
            "using --allow-existing."
        )

    # Create a NEW Flask app and configure its database before initializing
    # SQLAlchemy. This avoids reusing the main app's already-created engine.
    import_app = Flask("employee_performance_data_import")
    import_app.config.from_object(Config)
    import_app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{database_path.as_posix()}"
    )
    import_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(import_app)

    with import_app.app_context():
        try:
            actual_database = db.engine.url.database
            print(f"Import target database: {actual_database}")

            # Guard against accidentally targeting the main project database.
            if Path(actual_database).resolve() == (
                PROJECT_ROOT / "data" / "employee_performance.db"
            ).resolve():
                raise RuntimeError(
                    "Safety check failed: importer points to the main database."
                )

            db.create_all()

            total = 0
            for filename, model in IMPORT_ORDER:
                total += import_table(data_dir, filename, model)

            db.session.commit()
            print(f"\nImport completed successfully: {total:,} rows.")
            print(f"Source directory: {data_dir}")
            print(f"Database: {database_path}")
            print("Ground-truth anomaly labels were not imported.")

        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.remove()


if __name__ == "__main__":
    main()
