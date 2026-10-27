import csv
import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / os.environ.get(
    "VALIDATION_DATA_DIR", "generated"
)
def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_json(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def check_unique(rows, field, label, errors):
    values = [row.get(field, "") for row in rows]

    if any(not value for value in values):
        errors.append(f"{label}: one or more {field} values are empty")
        return

    if len(values) != len(set(values)):
        errors.append(f"{label}: duplicate {field} values")
    else:
        print(f"PASS: {label} IDs are unique")




def classify_expected_issue(message, ground_truth):
    """Return the matching ground-truth case ID, or None if unexpected."""
    expected_phrases = {
        "goal_owner_mismatch": ("owner mismatch",),
        "progress_out_of_range_without_rationale": (
            "progress outside 0-100 without rationale",
        ),
        "reviewer_relationship_invalid": (
            "reviewer is not assigned manager",
        ),
        "closed_cycle_silent_edit": (
            "closed-cycle edit has no reason",
        ),
        "feedback_untraceable": (
            "has invalid author",
            "has no evidence reference",
        ),
    }

    for case in ground_truth:
        case_id = case.get("case_id", "")
        record_id = case.get("record_id", "")
        anomaly_type = case.get("anomaly_type", "")
        phrases = expected_phrases.get(anomaly_type, ())

        if record_id and record_id in message and any(
            phrase in message for phrase in phrases
        ):
            return case_id

    return None


def main():
    errors = []
    warnings = []

    # 1. Load generated data.
    try:
        managers = load_csv("managers.csv")
        employees = load_csv("employees.csv")
        cycles = load_csv("review_cycles.csv")
        goals = load_csv("goals.csv")
        key_results = load_csv("key_results.csv")
        check_ins = load_csv("check_ins.csv")
        competencies = load_csv("competencies.csv")
        reviews = load_csv("reviews.csv")
        feedback = load_csv("feedback.csv")
        development_plans = load_csv("development_plans.csv")
        event_history = load_csv("event_history.csv")
        ground_truth = load_csv("ground_truth.csv")
        manifest = load_json("source_manifest.json")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: Cannot load generated data: {exc}")
        raise SystemExit(1)

    # 2. Check primary-key uniqueness.
    tables = [
        (managers, "manager_id", "Managers"),
        (employees, "employee_id", "Employees"),
        (cycles, "cycle_id", "Review cycles"),
        (goals, "goal_id", "Goals"),
        (key_results, "key_result_id", "Key results"),
        (check_ins, "check_in_id", "Check-ins"),
        (competencies, "competency_id", "Competencies"),
        (reviews, "review_id", "Reviews"),
        (feedback, "feedback_id", "Feedback"),
        (development_plans, "development_plan_id", "Development plans"),
        (event_history, "event_id", "Event history"),
    ]

    for rows, field, label in tables:
        check_unique(rows, field, label, errors)

    # 3. Build reference sets and lookup dictionaries.
    manager_ids = {row["manager_id"] for row in managers}
    employee_ids = {row["employee_id"] for row in employees}
    cycle_ids = {row["cycle_id"] for row in cycles}
    goal_ids = {row["goal_id"] for row in goals}
    competency_ids = {row["competency_id"] for row in competencies}
    review_ids = {row["review_id"] for row in reviews}

    employee_by_id = {
        row["employee_id"]: row for row in employees
    }
    cycle_by_id = {
        row["cycle_id"]: row for row in cycles
    }

    # 4. Validate employee-manager relationships.
    for row in employees:
        manager_id = row["manager_id"]

        if not manager_id or manager_id not in manager_ids:
            errors.append(
                f"Employee {row['employee_id']} has invalid manager"
            )

    # 5. Validate review cycle dates and statuses.
    allowed_cycle_statuses = {"planned", "active", "closed"}

    for row in cycles:
        try:
            start_date = row["start_date"]
            end_date = row["end_date"]

            if start_date > end_date:
                errors.append(
                    f"Cycle {row['cycle_id']} ends before it starts"
                )

            if row["status"] not in allowed_cycle_statuses:
                errors.append(
                    f"Cycle {row['cycle_id']} has invalid status"
                )
        except KeyError:
            errors.append("Review cycle is missing required date fields")

    # 6. Validate goals.
    allowed_goal_statuses = {
        "not_started", "in_progress", "completed"
    }

    for row in goals:
        goal_id = row["goal_id"]

        if row["employee_id"] not in employee_ids:
            errors.append(f"Goal {goal_id} has unknown employee")

        if row["cycle_id"] not in cycle_ids:
            errors.append(f"Goal {goal_id} has unknown cycle")

        if row["status"] not in allowed_goal_statuses:
            errors.append(f"Goal {goal_id} has invalid status")

        try:
            progress = int(row["progress_percent"])

            if not 0 <= progress <= 100:
                errors.append(
                    f"Goal {goal_id} progress outside 0-100"
                )
        except (ValueError, TypeError):
            errors.append(
                f"Goal {goal_id} progress is not a valid integer"
            )

    # 7. Validate key results.
    for row in key_results:
        key_id = row["key_result_id"]

        if row["goal_id"] not in goal_ids:
            errors.append(f"Key result {key_id} has unknown goal")

        try:
            current = float(row["current_value"])
            target = float(row["target_value"])

            if current < 0 or target <= 0 or current > target:
                errors.append(
                    f"Key result {key_id} has invalid numeric values"
                )
        except (ValueError, TypeError):
            errors.append(
                f"Key result {key_id} has nonnumeric values"
            )

    # 8. Validate check-ins.
    for row in check_ins:
        check_id = row["check_in_id"]

        if row["employee_id"] not in employee_ids:
            errors.append(f"Check-in {check_id} has unknown employee")

        if row["cycle_id"] not in cycle_ids:
            errors.append(f"Check-in {check_id} has unknown cycle")

        try:
            progress = int(row["progress_percent"])

            if not 0 <= progress <= 100:
                rationale = row.get("rationale", "").strip()

                if not rationale:
                    errors.append(
                        f"Check-in {check_id}: progress outside 0-100 "
                        "without rationale"
                    )
                else:
                    warnings.append(
                        f"Check-in {check_id}: progress outside 0-100 "
                        "has a rationale; review policy"
                    )
        except (ValueError, TypeError):
            errors.append(
                f"Check-in {check_id} progress is not an integer"
            )

    # 9. Validate reviews and reviewer relationships.
    for row in reviews:
        review_id = row["review_id"]
        employee = employee_by_id.get(row["employee_id"])

        if employee is None:
            errors.append(f"Review {review_id} has unknown employee")
            continue

        if row["cycle_id"] not in cycle_ids:
            errors.append(f"Review {review_id} has unknown cycle")

        reviewer_id = row["reviewer_id"]

        if reviewer_id not in manager_ids:
            errors.append(f"Review {review_id} has unknown reviewer")
        elif reviewer_id != employee["manager_id"]:
            errors.append(
                f"Review {review_id}: reviewer is not assigned manager"
            )

        if row["status"] not in {"draft", "submitted", "approved"}:
            errors.append(f"Review {review_id} has invalid status")

        try:
            score = int(row["score"])

            if not 1 <= score <= 5:
                errors.append(f"Review {review_id} score outside 1-5")
        except (ValueError, TypeError):
            errors.append(f"Review {review_id} score is not an integer")

    # 10. Validate feedback traceability.
    for row in feedback:
        feedback_id = row["feedback_id"]

        if row["employee_id"] not in employee_ids:
            errors.append(f"Feedback {feedback_id} has unknown employee")

        if row["competency_id"] not in competency_ids:
            errors.append(f"Feedback {feedback_id} has unknown competency")

        if row["cycle_id"] not in cycle_ids:
            errors.append(f"Feedback {feedback_id} has unknown cycle")

        author_id = row.get("author_id", "").strip()
        feedback_type = row.get("feedback_type", "").strip().lower()
        employee_id = row.get("employee_id", "").strip()

        if feedback_type == "manager":
            valid_author = author_id in manager_ids
        elif feedback_type == "self":
            valid_author = (
                author_id == employee_id
                and author_id in employee_ids
            )
        elif feedback_type == "peer":
            valid_author = (
                author_id in employee_ids
                and author_id != employee_id
            )
        else:
            valid_author = False

        if not valid_author:
            errors.append(f"Feedback {feedback_id} has invalid author")

        if not row.get("evidence_reference", "").strip():
            errors.append(
                f"Feedback {feedback_id} has no evidence reference"
            )

        try:
            rating = int(row["rating"])

            if not 1 <= rating <= 5:
                errors.append(f"Feedback {feedback_id} rating outside 1-5")
        except (ValueError, TypeError, KeyError):
            errors.append(f"Feedback {feedback_id} has invalid rating")

    # 11. Validate development plan relationships.
    for row in development_plans:
        plan_id = row["development_plan_id"]

        if row["employee_id"] not in employee_ids:
            errors.append(f"Development plan {plan_id} has unknown employee")

        if row["review_id"] not in review_ids:
            errors.append(f"Development plan {plan_id} has unknown review")

    # 12. Validate goal-owner anomaly using the documented ID convention.
    # Expected format: GOAL-<original employee ID>-<sequence>
    for row in goals:
        goal_id = row["goal_id"]
        match = re.fullmatch(r"GOAL-(EMP-\d{6})-\d{5}", goal_id)

        if not match:
            errors.append(f"Goal {goal_id} has invalid ID format")
            continue

        original_owner_id = match.group(1)

        if original_owner_id != row["employee_id"]:
            errors.append(
                f"Goal {goal_id} owner mismatch: ID encodes "
                f"{original_owner_id}, record names {row['employee_id']}"
            )

    # 13. Validate event history and closed-cycle edits.
    for row in event_history:
        event_id = row["event_id"]
        cycle_id = row["cycle_id"]

        if cycle_id not in cycle_ids:
            errors.append(f"Event {event_id} has unknown cycle")
            continue

        cycle = cycle_by_id[cycle_id]

        if (
            cycle["status"] == "closed"
            and row["event_type"] == "updated"
            and not row.get("reason", "").strip()
        ):
            errors.append(
                f"Event {event_id}: closed-cycle edit has no reason"
            )

        if not row.get("actor_id", "").strip():
            errors.append(f"Event {event_id} has no actor")

    # 14. Validate ground-truth cases and record references.
    expected_cases = {
        "goal_owner_mismatch",
        "progress_out_of_range_without_rationale",
        "reviewer_relationship_invalid",
        "closed_cycle_silent_edit",
        "feedback_untraceable",
    }

    actual_cases = {row["anomaly_type"] for row in ground_truth}

    if actual_cases != expected_cases:
        errors.append(
            "Ground truth must contain exactly the five expected anomaly types"
        )
    else:
        print("PASS: all five expected ground-truth types are present")

    table_by_type = {
        "goal": {row["goal_id"] for row in goals},
        "check_in": {row["check_in_id"] for row in check_ins},
        "review": {row["review_id"] for row in reviews},
        "event_history": {row["event_id"] for row in event_history},
        "feedback": {row["feedback_id"] for row in feedback},
    }

    for case in ground_truth:
        record_ids = table_by_type.get(case["entity_type"])

        if record_ids is None:
            errors.append(
                f"Ground truth {case['case_id']} has unknown entity type"
            )
        elif case["record_id"] not in record_ids:
            errors.append(
                f"Ground truth {case['case_id']} references missing record"
            )

        if case["expected_label"] != "invalid":
            errors.append(
                f"Ground truth {case['case_id']} has unexpected label"
            )

    # 15. Compare generated row counts against the manifest.
    manifest_counts = manifest.get("counts", {})

    actual_counts = {
        "employees": len(employees),
        "managers": len(managers),
        "goals": len(goals),
        "key_results": len(key_results),
        "check_ins": len(check_ins),
        "competencies": len(competencies),
        "reviews": len(reviews),
        "feedback": len(feedback),
        "development_plans": len(development_plans),
        "event_history": len(event_history),
        "ground_truth_cases": len(ground_truth),
    }

    for name, actual_count in actual_counts.items():
        expected_count = manifest_counts.get(name)

        if expected_count is not None and expected_count != actual_count:
            errors.append(
                f"Manifest count mismatch for {name}: "
                f"expected {expected_count}, got {actual_count}"
            )

    # 16. Print summary.
    print("\nValidation summary")
    print("------------------")

    for name, count in actual_counts.items():
        print(f"{name}: {count}")

    if warnings:
        print(f"\nWarnings: {len(warnings)}")

        for warning in warnings:
            print("WARNING:", warning)

    # 17. Separate deliberate edge-case findings from unexpected failures.
    expected_findings = []
    unexpected_findings = []

    for error in errors:
        case_id = classify_expected_issue(error, ground_truth)
        if case_id:
            expected_findings.append((case_id, error))
        else:
            unexpected_findings.append(error)

    detected_case_ids = {case_id for case_id, _ in expected_findings}
    expected_case_ids = {row.get("case_id", "") for row in ground_truth}
    missing_case_ids = expected_case_ids - detected_case_ids

    print("\\nEdge-case detection report")
    print("--------------------------")
    print(f"Ground-truth cases: {len(expected_case_ids)}")
    print(f"Cases detected: {len(detected_case_ids)}")
    print(f"Expected findings: {len(expected_findings)}")
    print(f"Unexpected findings: {len(unexpected_findings)}")

    if expected_findings:
        print("\\nExpected findings (deliberately injected test cases):")
        for case_id, message in expected_findings:
            print(f"EXPECTED [{case_id}]: {message}")

    if missing_case_ids:
        print("\\nGround-truth cases not detected:")
        for case_id in sorted(missing_case_ids):
            print(f"MISSING: {case_id}")

    if unexpected_findings:
        print("\\nUnexpected validation failures:")
        for message in unexpected_findings:
            print("UNEXPECTED:", message)

    print("\\nValidation sections executed: 17")
    print("Note: section count is not the same as the number of individual checks.")

    if unexpected_findings or missing_case_ids:
        print("\\nRESULT: REVIEW REQUIRED")
        raise SystemExit(1)

    print("\\nRESULT: PASS — all ground-truth cases were detected, "
          "with no unexpected findings.")


if __name__ == "__main__":
    main()
