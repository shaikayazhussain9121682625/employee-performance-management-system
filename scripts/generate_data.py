import argparse
import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from faker import Faker

SEED = 20261022
AS_OF_DATE = date(2026, 10, 26)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "generated"


def write_csv(filename, rows):
    """Write a list of dictionaries to CSV using a stable column order."""
    path = DATA_DIR / filename
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def random_date(rng, start, end):
    """Return a reproducible ISO date between start and end, inclusive."""
    if start > end:
        raise ValueError(f"Invalid date range: {start} is after {end}")
    span = (end - start).days
    return start + timedelta(days=rng.randint(0, span))


def date_in_cycle(rng, cycle):
    """Pick a date inside the cycle and not later than the reference date."""
    start = date.fromisoformat(cycle["start_date"])
    end = min(date.fromisoformat(cycle["end_date"]), AS_OF_DATE)
    return random_date(rng, start, end).isoformat()


def generate(args):
    rng = random.Random(args.seed)
    fake = Faker()
    fake.seed_instance(args.seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    departments = [
        "Engineering",
        "Product",
        "Human Resources",
        "Finance",
        "Sales",
        "Customer Support",
    ]
    job_titles = [
        "Software Engineer",
        "Data Analyst",
        "Product Manager",
        "HR Specialist",
        "Sales Executive",
        "Support Specialist",
    ]

    # 1. Managers
    managers = []
    for i in range(1, args.managers + 1):
        managers.append({
            "manager_id": f"MGR-{i:06d}",
            "full_name": fake.name(),
            "email": f"manager{i:06d}@example.com",
            "department": departments[(i - 1) % len(departments)],
        })

    # 2. Employees. Hire dates are before both 2026 review cycles.
    employees = []
    for i in range(1, args.employees + 1):
        manager = managers[(i - 1) % len(managers)]
        hire_date = random_date(
            rng, date(2020, 1, 1), date(2025, 12, 31)
        )
        employees.append({
            "employee_id": f"EMP-{i:06d}",
            "full_name": fake.name(),
            "email": f"employee{i:06d}@example.com",
            "department": departments[(i - 1) % len(departments)],
            "job_title": job_titles[(i - 1) % len(job_titles)],
            "hire_date": hire_date.isoformat(),
            "employment_status": rng.choices(
                ["active", "inactive"], weights=[9, 1], k=1
            )[0],
            "manager_id": manager["manager_id"],
        })

    # 3. Review cycles. H2 ends in December, but generated activity only
    # occurs up to AS_OF_DATE, so we never create future events.
    cycles = [
        {
            "cycle_id": "CYCLE-2026-H1",
            "name": "2026 First Half",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "status": "closed",
        },
        {
            "cycle_id": "CYCLE-2026-H2",
            "name": "2026 Second Half",
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "status": "active",
        },
    ]

    # 4. Goals and key results. Goal progress is calculated from the
    # average progress of its two key results, rather than randomized twice.
    goals = []
    key_results = []
    per_employee_goal_count = {}
    for i in range(1, args.goals + 1):
        employee = employees[(i - 1) % len(employees)]
        cycle = cycles[(i - 1) % len(cycles)]
        per_employee_goal_count[employee["employee_id"]] = (
            per_employee_goal_count.get(employee["employee_id"], 0) + 1
        )
        sequence = per_employee_goal_count[employee["employee_id"]]
        goal_id = f"GOAL-{employee['employee_id']}-{sequence:05d}"

        key_result_values = [rng.randint(0, 100), rng.randint(0, 100)]
        progress = round(sum(key_result_values) / len(key_result_values))
        if progress == 0:
            status = "not_started"
        elif progress == 100:
            status = "completed"
        else:
            status = "in_progress"

        goals.append({
            "goal_id": goal_id,
            "employee_id": employee["employee_id"],
            "cycle_id": cycle["cycle_id"],
            "title": f"Performance goal {i}",
            "status": status,
            "progress_percent": progress,
            "created_date": date_in_cycle(rng, cycle),
        })

        for k, current_value in enumerate(key_result_values, start=1):
            key_results.append({
                "key_result_id": f"KR-{goal_id}-{k:02d}",
                "goal_id": goal_id,
                "description": f"Measurable result {k} for goal {i}",
                "target_value": 100,
                "current_value": current_value,
                "unit": "percent",
            })

    # 5. Check-ins. Each check-in is dated inside the employee's cycle.
    check_ins = []
    for i in range(1, args.checkins + 1):
        employee = employees[(i - 1) % len(employees)]
        cycle = cycles[(i - 1) % len(cycles)]
        check_ins.append({
            "check_in_id": f"CHK-{i:06d}",
            "employee_id": employee["employee_id"],
            "cycle_id": cycle["cycle_id"],
            "check_in_date": date_in_cycle(rng, cycle),
            "progress_percent": rng.randint(0, 100),
            "notes": f"Progress update {i}",
            "rationale": "Routine progress update",
        })

    # 6. Competencies
    competency_names = [
        "Communication",
        "Teamwork",
        "Problem Solving",
        "Ownership",
        "Technical Skills",
        "Planning",
        "Adaptability",
        "Leadership",
    ]
    competencies = [
        {
            "competency_id": f"COMP-{i:03d}",
            "name": name,
            "description": f"Measures employee {name.lower()}",
        }
        for i, name in enumerate(competency_names, start=1)
    ]

    # 7. Reviews. One review per employee, with the assigned manager as reviewer.
    reviews = []
    for i, employee in enumerate(employees, start=1):
        cycle = cycles[(i - 1) % len(cycles)]
        reviews.append({
            "review_id": f"REV-2026-{i:06d}",
            "employee_id": employee["employee_id"],
            "cycle_id": cycle["cycle_id"],
            "reviewer_id": employee["manager_id"],
            "score": rng.randint(1, 5),
            "status": rng.choice(["draft", "submitted", "approved"]),
            "review_date": date_in_cycle(rng, cycle),
        })

    # 8. Feedback. Author is the assigned manager; dates match the cycle.
    feedback = []
    for i in range(1, args.feedback + 1):
        employee = employees[(i - 1) % len(employees)]
        cycle = cycles[(i - 1) % len(cycles)]
        competency = competencies[(i - 1) % len(competencies)]
        feedback.append({
            "feedback_id": f"FDB-{i:06d}",
            "employee_id": employee["employee_id"],
            "competency_id": competency["competency_id"],
            "cycle_id": cycle["cycle_id"],
            "author_id": employee["manager_id"],
            "evidence_reference": f"EVID-{i:06d}",
            "rating": rng.randint(1, 5),
            "comments": f"Evidence-based feedback {i}",
            "feedback_date": date_in_cycle(rng, cycle),
        })

    # 9. Development plans
    development_plans = []
    for i, review in enumerate(reviews, start=1):
        development_plans.append({
            "development_plan_id": f"DP-{i:06d}",
            "employee_id": review["employee_id"],
            "review_id": review["review_id"],
            "objective": "Improve one measurable work skill",
            "action": "Complete a learning activity and discuss progress",
            "target_date": "2026-12-15",
            "status": "planned",
        })

    # 10. Audit/event history baseline
    event_history = [{
        "event_id": "EVT-000001",
        "cycle_id": "CYCLE-2026-H2",
        "entity_type": "goal",
        "record_id": goals[0]["goal_id"] if goals else "",
        "event_type": "created",
        "actor_id": goals[0]["employee_id"] if goals else "",
        "event_time": "2026-10-01T09:00:00",
        "reason": "Initial goal creation",
    }]

    # Inject the labelled edge cases into the data that will be submitted.
    # Ground truth is stored separately from the entity tables.
    ground_truth = []

    if goals and len(employees) > 1:
        original_owner = goals[0]["employee_id"]
        other_employee = employees[1]["employee_id"]
        goals[0]["employee_id"] = other_employee
        ground_truth.append({
            "case_id": "EDGE-001",
            "entity_type": "goal",
            "record_id": goals[0]["goal_id"],
            "anomaly_type": "goal_owner_mismatch",
            "expected_label": "invalid",
            "description": (
                f"Goal ID belongs to {original_owner}, but employee_id "
                f"was changed to {other_employee}."
            ),
        })

    if check_ins:
        check_ins[0]["progress_percent"] = 140
        check_ins[0]["rationale"] = ""
        ground_truth.append({
            "case_id": "EDGE-002",
            "entity_type": "check_in",
            "record_id": check_ins[0]["check_in_id"],
            "anomaly_type": "progress_out_of_range_without_rationale",
            "expected_label": "invalid",
            "description": "Progress exceeds 100 without a rationale.",
        })

    if reviews and len(managers) > 1:
        employee = employees[0]
        wrong_manager = next(
            manager for manager in managers
            if manager["manager_id"] != employee["manager_id"]
        )
        reviews[0]["reviewer_id"] = wrong_manager["manager_id"]
        ground_truth.append({
            "case_id": "EDGE-003",
            "entity_type": "review",
            "record_id": reviews[0]["review_id"],
            "anomaly_type": "reviewer_relationship_invalid",
            "expected_label": "invalid",
            "description": "Reviewer is not the employee's assigned manager.",
        })

    if event_history:
        event_history.append({
            "event_id": "EVT-000002",
            "cycle_id": "CYCLE-2026-H1",
            "entity_type": "goal",
            "record_id": goals[0]["goal_id"] if goals else "",
            "event_type": "updated",
            "actor_id": "MGR-000001",
            "event_time": "2026-10-02T10:00:00",
            "reason": "",
        })
        ground_truth.append({
            "case_id": "EDGE-004",
            "entity_type": "event_history",
            "record_id": "EVT-000002",
            "anomaly_type": "closed_cycle_silent_edit",
            "expected_label": "invalid",
            "description": "A closed-cycle record was edited without a reason.",
        })

    if feedback:
        feedback[0]["author_id"] = ""
        feedback[0]["evidence_reference"] = ""
        ground_truth.append({
            "case_id": "EDGE-005",
            "entity_type": "feedback",
            "record_id": feedback[0]["feedback_id"],
            "anomaly_type": "feedback_untraceable",
            "expected_label": "invalid",
            "description": "Feedback has no author or evidence reference.",
        })

    # Write all tables after anomaly injection so output files match ground truth.
    output_tables = {
        "managers.csv": managers,
        "employees.csv": employees,
        "review_cycles.csv": cycles,
        "goals.csv": goals,
        "key_results.csv": key_results,
        "check_ins.csv": check_ins,
        "competencies.csv": competencies,
        "reviews.csv": reviews,
        "feedback.csv": feedback,
        "development_plans.csv": development_plans,
        "event_history.csv": event_history,
        "ground_truth.csv": ground_truth,
    }
    for filename, rows in output_tables.items():
        write_csv(filename, rows)

    with (DATA_DIR / "ground_truth.json").open("w", encoding="utf-8") as file:
        json.dump(ground_truth, file, indent=2)

    manifest = {
        "seed": args.seed,
        "reference_date": AS_OF_DATE.isoformat(),
        "data_type": "synthetic",
        "generator_version": "2.0",
        "counts": {
            "managers": len(managers),
            "employees": len(employees),
            "goals": len(goals),
            "key_results": len(key_results),
            "check_ins": len(check_ins),
            "competencies": len(competencies),
            "reviews": len(reviews),
            "feedback": len(feedback),
            "development_plans": len(development_plans),
            "event_history": len(event_history),
            "ground_truth_cases": len(ground_truth),
        },
        "notes": [
            "All records are synthetic.",
            "Ground truth labels deliberately injected edge cases.",
            "Goal progress is derived from its key-result current values.",
            "Dates are generated within their assigned review-cycle windows.",
        ],
    }
    with (DATA_DIR / "source_manifest.json").open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)

    print("Data generation complete.")
    print(json.dumps(manifest["counts"], indent=2))
    print(f"Seed: {args.seed}")
    print(f"Reference date: {AS_OF_DATE.isoformat()}")
    print(f"Output directory: {DATA_DIR}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate deterministic synthetic performance-management data."
    )
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--employees", type=int, default=20)
    parser.add_argument("--managers", type=int, default=5)
    parser.add_argument("--goals", type=int, default=50)
    parser.add_argument("--checkins", type=int, default=100)
    parser.add_argument("--feedback", type=int, default=50)
    args = parser.parse_args()

    if min(args.employees, args.managers, args.goals, args.checkins, args.feedback) < 1:
        parser.error("All counts must be at least 1.")
    if args.employees < 2:
        parser.error("Use at least 2 employees to generate the goal-owner edge case.")
    if args.managers < 2:
        parser.error("Use at least 2 managers to generate the reviewer edge case.")

    generate(args)


if __name__ == "__main__":
    main()
