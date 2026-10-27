
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "employee_performance.db"
BACKUP_PATH = PROJECT_ROOT / "data" / "employee_performance_backup.db"


def get_columns(connection, table_name):
    rows = connection.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()
    return {row[1] for row in rows}


def migrate():
    if not DATABASE_PATH.exists():
        raise SystemExit(f"Database not found: {DATABASE_PATH}")

    if not BACKUP_PATH.exists():
        raise SystemExit(
            f"Backup not found: {BACKUP_PATH}. "
            "Create a backup before migrating."
        )

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = OFF")

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

        required_tables = {
            "managers",
            "employees",
            "feedback",
            "development_plans",
        }

        missing_tables = required_tables - tables

        if missing_tables:
            raise RuntimeError(
                f"Required tables are missing: {sorted(missing_tables)}"
            )

        with connection:
            # Feedback category.
            feedback_columns = get_columns(connection, "feedback")

            if "feedback_type" not in feedback_columns:
                connection.execute("""
                    ALTER TABLE feedback
                    ADD COLUMN feedback_type VARCHAR(20)
                    NOT NULL DEFAULT 'manager'
                """)
                print("Added feedback.feedback_type")
            else:
                print("feedback.feedback_type already exists")

            # Development-plan approval workflow.
            plan_columns = get_columns(
                connection, "development_plans"
            )

            if "approval_status" not in plan_columns:
                connection.execute("""
                    ALTER TABLE development_plans
                    ADD COLUMN approval_status VARCHAR(20)
                    NOT NULL DEFAULT 'pending'
                """)
                print("Added development_plans.approval_status")
            else:
                print("development_plans.approval_status already exists")

            if "approved_by" not in plan_columns:
                connection.execute("""
                    ALTER TABLE development_plans
                    ADD COLUMN approved_by VARCHAR(20)
                    REFERENCES managers(manager_id)
                """)
                print("Added development_plans.approved_by")
            else:
                print("development_plans.approved_by already exists")

            if "approved_at" not in plan_columns:
                connection.execute("""
                    ALTER TABLE development_plans
                    ADD COLUMN approved_at DATETIME
                """)
                print("Added development_plans.approved_at")
            else:
                print("development_plans.approved_at already exists")

            # Effective-dated manager assignment history.
            connection.execute("""
                CREATE TABLE IF NOT EXISTS manager_assignment_history (
                    assignment_id VARCHAR(30) PRIMARY KEY,
                    employee_id VARCHAR(20) NOT NULL,
                    manager_id VARCHAR(20) NOT NULL,
                    effective_from DATE NOT NULL,
                    effective_to DATE,
                    reason TEXT,
                    recorded_at DATETIME NOT NULL,
                    FOREIGN KEY (employee_id)
                        REFERENCES employees(employee_id),
                    FOREIGN KEY (manager_id)
                        REFERENCES managers(manager_id),
                    CHECK (
                        effective_to IS NULL
                        OR effective_to >= effective_from
                    )
                )
            """)

            print("Created or verified manager_assignment_history")

        connection.execute("PRAGMA foreign_keys = ON")

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            print(
                f"WARNING: Found {len(violations)} foreign-key "
                "violation(s). Do not ignore these."
            )
            for violation in violations[:10]:
                print(violation)
        else:
            print("Foreign-key check passed")

        print("\nMigration completed.")
        print("Existing records were not deleted.")
        print(f"Database: {DATABASE_PATH}")

    finally:
        connection.close()


if __name__ == "__main__":
    migrate()
