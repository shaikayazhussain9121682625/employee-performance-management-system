
import sys
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app import app
from extensions import db
import models


EXPECTED_COUNTS = {
    "managers": (models.Manager, 500),
    "employees": (models.Employee, 3000),
    "review_cycles": (models.ReviewCycle, 2),
    "competencies": (models.Competency, 8),
    "goals": (models.Goal, 10000),
    "key_results": (models.KeyResult, 20000),
    "check_ins": (models.CheckIn, 20000),
    "reviews": (models.Review, 3000),
    "feedback": (models.Feedback, 5000),
    "development_plans": (models.DevelopmentPlan, 3000),
    # Audit history grows as legitimate changes are recorded.
    "event_history": (models.EventHistory, None),
}


def main():
    failures = 0

    with app.app_context():
        print("DATABASE RECORD COUNTS")
        print("----------------------")

        for name, (model, expected) in EXPECTED_COUNTS.items():
            actual = db.session.query(model).count()

            if expected is None:
                # Preserve the minimum expected baseline history.
                passed = actual >= 2
                expected_text = "at least 2 baseline records"
            else:
                passed = actual == expected
                expected_text = f"expected {expected}"

            status = "PASS" if passed else "FAIL"

            print(
                f"{status}: {name}: {actual} records "
                f"({expected_text})"
            )

            if not passed:
                failures += 1

        print("\nFOREIGN KEY CHECK")
        print("-----------------")

        violations = db.session.execute(
            db.text("PRAGMA foreign_key_check")
        ).all()

        if violations:
            failures += 1
            print(f"FAIL: {len(violations)} foreign-key violations")

            for violation in violations[:20]:
                print(violation)
        else:
            print("PASS: No foreign-key violations detected")

        print("\nGROUND-TRUTH FILE")
        print("-----------------")

        ground_truth_path = (
            PROJECT_ROOT / "data" / "generated" / "ground_truth.csv"
        )

        if not ground_truth_path.exists():
            failures += 1
            print("FAIL: ground_truth.csv not found")
        else:
            with ground_truth_path.open(
                "r", newline="", encoding="utf-8-sig"
            ) as file:
                cases = list(csv.DictReader(file))

            if len(cases) != 5:
                failures += 1
                print(
                    "FAIL: Expected 5 ground-truth cases, "
                    f"found {len(cases)}"
                )
            else:
                print("PASS: 5 ground-truth cases preserved")

            print(
                "Ground truth remains separate from application tables."
            )

        print("\nFINAL RESULT")
        print("------------")

        if failures:
            print(f"FAIL: {failures} verification issue(s) found.")
            raise SystemExit(1)

        print("PASS: Database counts and foreign-key checks succeeded.")


if __name__ == "__main__":
    main()
