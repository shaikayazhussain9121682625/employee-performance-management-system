import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app import app
from models import Goal, KeyResult

with app.app_context():
    goals = Goal.query.order_by(Goal.goal_id).all()
    key_results = KeyResult.query.order_by(KeyResult.goal_id).all()

    results_by_goal = defaultdict(list)
    for result in key_results:
        results_by_goal[result.goal_id].append(result)

    missing = 0
    mismatches = []

    for goal in goals:
        results = results_by_goal.get(goal.goal_id, [])

        if not results:
            missing += 1
            continue

        # Match the generator's original formula exactly.
        derived = round(
            sum(result.current_value for result in results) / len(results)
        )

        if abs(derived - goal.progress_percent) > 0.01:
            mismatches.append(
                (goal.goal_id, goal.progress_percent, derived)
            )

    print("Goals checked:", len(goals))
    print("Key results checked:", len(key_results))
    print("Goals without key results:", missing)
    print("Mismatches using generator formula:", len(mismatches))
    print("First mismatches:", mismatches[:10])

    if missing or mismatches:
        print("RESULT: REVIEW REQUIRED")
        sys.exit(1)

    print("RESULT: PASS")
