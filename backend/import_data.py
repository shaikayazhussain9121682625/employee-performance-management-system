
import csv
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app import app
from extensions import db
import models

DATA_DIR = PROJECT_ROOT / "data" / "generated"

# CSV filename and matching SQLAlchemy model.
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
]

# Explicitly map CSV columns to model attributes.
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
}


def convert_value(value, column):
    if value == "":
        return None

    column_type = column.type.python_type

    if column_type is date:
        return date.fromisoformat(value)

    if column_type is datetime:
        return datetime.fromisoformat(value)

    if column_type is int:
        return int(value)

    if column_type is float:
        return float(value)

    return value


def import_table(filename, model):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing required CSV: {path}")

    mapping = COLUMN_MAP[filename]
    columns = {column.name: column for column in model.__table__.columns}
    count = 0

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        missing = set(mapping) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{filename} is missing required columns: {sorted(missing)}"
            )

        for row in reader:
            record = {}

            for csv_column, model_column in mapping.items():
                column = columns[model_column]
                value = convert_value(row[csv_column], column)

                if value is None and not column.nullable and column.default is None:
                    raise ValueError(
                        f"{filename}, row {reader.line_num}: "
                        f"required field {csv_column} is empty"
                    )

                record[model_column] = value

            db.session.add(model(**record))
            count += 1

            if count % 1000 == 0:
                db.session.flush()

    db.session.flush()
    print(f"Imported {count} rows from {filename}")
    return count


def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    with app.app_context():
        try:
            db.create_all()
            total = 0

            for filename, model in IMPORT_ORDER:
                total += import_table(filename, model)

            db.session.commit()
            print(f"\nImport completed successfully: {total:,} rows.")

        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()
